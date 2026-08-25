from io import BytesIO
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.db.models.document import Document
from app.db.models.extraction_result import ExtractionResult
from app.db.models.ocr_result import OCRResult
from app.exceptions.extraction_exceptions import ExtractionException
from app.exceptions.ocr_exceptions import OCRException


def test_process_document_persists_results(
    client: TestClient,
    db_session,
):
    fake_ocr_response = type(
        "FakeOCRResponse",
        (),
        {
            "page_count": 1,
            "pages": [
                type(
                    "FakeOCRPage",
                    (),
                    {
                        "page_number": 1,
                        "extracted_text": (
                            "Invoice Number: INV-001\n"
                            "Total: 1500"
                        ),
                        "average_confidence": 95.0,
                    },
                )()
            ],
            "processing_time": 0.25,
        },
    )()

    fake_extraction_response = {
        "document_type": "invoice",
        "fields": {
            "invoice_number": "INV-001",
            "total": 1500,
        },
        "overall_confidence": 0.95,
        "requires_review": False,
    }

    with patch(
        "app.services.document_processing_service.OCRService.process_pdf",
        new_callable=AsyncMock,
        return_value=fake_ocr_response,
    ), patch(
        "app.services.document_processing_service.ExtractionService.extract",
        return_value=fake_extraction_response,
    ):
        response = client.post(
            "/api/v1/documents/process",
            files={
                "file": (
                    "invoice.pdf",
                    BytesIO(b"%PDF-1.4 fake pdf content"),
                    "application/pdf",
                )
            },
            data={
                "document_type": "invoice",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["document_type"] == "invoice"
    assert data["fields"]["invoice_number"] == "INV-001"
    assert data["fields"]["total"] == 1500
    assert data["overall_confidence"] == 0.95
    assert data["requires_review"] is False

    assert "document_id" in data

    document_id = data["document_id"]

    # ------------------------------------------------------------
    # Verify real PostgreSQL persistence
    # ------------------------------------------------------------

    document = db_session.get(
        Document,
        document_id,
    )

    assert document is not None
    assert document.original_filename == "invoice.pdf"
    assert document.content_type == "application/pdf"
    assert document.status == "extraction_complete"

    ocr_result = (
        db_session.query(OCRResult)
        .filter(
            OCRResult.document_id == document_id
        )
        .first()
    )

    assert ocr_result is not None
    assert ocr_result.page_count == 1
    assert "INV-001" in ocr_result.full_text
    assert ocr_result.average_confidence == 95.0

    extraction_result = (
        db_session.query(ExtractionResult)
        .filter(
            ExtractionResult.document_id == document_id
        )
        .first()
    )

    assert extraction_result is not None
    assert extraction_result.document_type == "invoice"
    assert extraction_result.fields["invoice_number"] == "INV-001"
    assert extraction_result.fields["total"] == 1500
    assert extraction_result.overall_confidence == 0.95
    assert extraction_result.requires_review is False


# ------------------------------------------------------------------
# OCR failure
# ------------------------------------------------------------------


def test_process_document_handles_ocr_failure(
    client: TestClient,
    db_session,
):
    with patch(
        "app.services.document_processing_service.OCRService.process_pdf",
        new_callable=AsyncMock,
        side_effect=OCRException("OCR engine failed"),
    ):
        response = client.post(
            "/api/v1/documents/process",
            files={
                "file": (
                    "invoice.pdf",
                    BytesIO(b"%PDF-1.4 fake pdf content"),
                    "application/pdf",
                )
            },
        )

    assert response.status_code == 500

    data = response.json()

    assert data["stage"] == "ocr"
    assert "OCR stage failed" in data["detail"]

    # --------------------------------------------------------------
    # Verify document was persisted and marked as failed
    # --------------------------------------------------------------

    document = (
        db_session.query(Document)
        .order_by(Document.created_at.desc())
        .first()
    )

    assert document is not None
    assert document.original_filename == "invoice.pdf"
    assert document.status == "failed"

    # OCR result must not exist
    ocr_result = (
        db_session.query(OCRResult)
        .filter(
            OCRResult.document_id == document.id
        )
        .first()
    )

    assert ocr_result is None

    # Extraction result must not exist
    extraction_result = (
        db_session.query(ExtractionResult)
        .filter(
            ExtractionResult.document_id == document.id
        )
        .first()
    )

    assert extraction_result is None


# ------------------------------------------------------------------
# Extraction failure
# ------------------------------------------------------------------


def test_process_document_handles_extraction_failure(
    client: TestClient,
    db_session,
):
    fake_ocr_response = type(
        "FakeOCRResponse",
        (),
        {
            "page_count": 1,
            "pages": [
                type(
                    "FakeOCRPage",
                    (),
                    {
                        "page_number": 1,
                        "extracted_text": (
                            "Invoice Number: INV-002\n"
                            "Total: 2500"
                        ),
                        "average_confidence": 92.0,
                    },
                )()
            ],
            "processing_time": 0.30,
        },
    )()

    with patch(
        "app.services.document_processing_service.OCRService.process_pdf",
        new_callable=AsyncMock,
        return_value=fake_ocr_response,
    ), patch(
        "app.services.document_processing_service.ExtractionService.extract",
        side_effect=ExtractionException(
            "Extraction engine failed"
        ),
    ):
        response = client.post(
            "/api/v1/documents/process",
            files={
                "file": (
                    "invoice.pdf",
                    BytesIO(b"%PDF-1.4 fake pdf content"),
                    "application/pdf",
                )
            },
            data={
                "document_type": "invoice",
            },
        )

    assert response.status_code == 500

    data = response.json()

    assert data["stage"] == "extraction"
    assert "Extraction stage failed" in data["detail"]

    document = (
        db_session.query(Document)
        .order_by(Document.created_at.desc())
        .first()
    )

    assert document is not None
    assert document.original_filename == "invoice.pdf"
    assert document.status == "failed"

    # OCR succeeded, so its result must exist.
    ocr_result = (
        db_session.query(OCRResult)
        .filter(
            OCRResult.document_id == document.id
        )
        .first()
    )

    assert ocr_result is not None
    assert ocr_result.page_count == 1
    assert "INV-002" in ocr_result.full_text
    assert ocr_result.average_confidence == 92.0

    # Extraction failed, so no extraction result should exist.
    extraction_result = (
        db_session.query(ExtractionResult)
        .filter(
            ExtractionResult.document_id == document.id
        )
        .first()
    )

    assert extraction_result is None