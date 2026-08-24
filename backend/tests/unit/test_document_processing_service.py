from io import BytesIO
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException, UploadFile

from app.exceptions.extraction_exceptions import ExtractionException
from app.exceptions.ocr_exceptions import OCRException
from app.exceptions.pipeline_exceptions import (
    PipelineExtractionStageError,
    PipelineOCRStageError,
)
from app.schemas.ocr import OCRPage, OCRResponse
from app.services.document_processing_service import (
    DocumentProcessingService,
)


def create_upload_file(
    filename: str = "invoice.pdf",
    content_type: str = "application/pdf",
) -> UploadFile:
    return UploadFile(
        filename=filename,
        file=BytesIO(b"fake pdf content"),
        headers={"content-type": content_type},
    )


def create_document():
    return SimpleNamespace(
        id="document-123",
    )


def create_ocr_response():
    return OCRResponse(
        filename="invoice.pdf",
        page_count=2,
        pages=[
            OCRPage(
                page_number=1,
                extracted_text="Invoice Number INV-001",
                average_confidence=90.0,
            ),
            OCRPage(
                page_number=2,
                extracted_text="Total Amount 1500",
                average_confidence=80.0,
            ),
        ],
        processing_time=1.25,
        status="success",
    )


def create_extraction_result():
    return {
        "document_type": "invoice",
        "fields": [
            {
                "field_name": "invoice_number",
                "value": "INV-001",
                "confidence": 0.95,
                "source_text": "Invoice Number INV-001",
            }
        ],
        "overall_confidence": 0.92,
        "requires_review": False,
    }


def create_service():
    document_repo = MagicMock()
    ocr_repo = MagicMock()
    extraction_repo = MagicMock()

    service = DocumentProcessingService(
        document_repo=document_repo,
        ocr_repo=ocr_repo,
        extraction_repo=extraction_repo,
    )

    service.ocr_service = MagicMock()
    service.ocr_service.process_pdf = AsyncMock()

    service.extraction_service = MagicMock()

    return (
        service,
        document_repo,
        ocr_repo,
        extraction_repo,
    )


@pytest.mark.asyncio
async def test_process_pdf_success():
    (
        service,
        document_repo,
        ocr_repo,
        extraction_repo,
    ) = create_service()

    document = create_document()
    ocr_result = create_ocr_response()
    extraction_result = create_extraction_result()

    document_repo.create.return_value = document

    service.ocr_service.process_pdf = AsyncMock(
        return_value=ocr_result
    )

    service.extraction_service.extract.return_value = (
        extraction_result
    )

    file = create_upload_file()

    result = await service.process_pdf(
        file=file,
        document_type="invoice",
    )

    assert result["document_type"] == "invoice"
    assert result["overall_confidence"] == 0.92
    assert result["requires_review"] is False
    assert result["document_id"] == "document-123"

    document_repo.create.assert_called_once_with(
        original_filename="invoice.pdf",
        content_type="application/pdf",
        file_size=0,
    )

    service.ocr_service.process_pdf.assert_awaited_once_with(
        file
    )

    extraction_text = (
        "Invoice Number INV-001\n\n"
        "Total Amount 1500"
    )

    service.extraction_service.extract.assert_called_once_with(
        document_text=extraction_text,
        document_type="invoice",
    )

    ocr_repo.create.assert_called_once_with(
        document_id="document-123",
        page_count=2,
        full_text=extraction_text,
        average_confidence=85.0,
        processing_time=1.25,
    )

    extraction_repo.create.assert_called_once_with(
        document_id="document-123",
        document_type="invoice",
        fields=extraction_result["fields"],
        overall_confidence=0.92,
        requires_review=False,
    )

    assert document_repo.update_status.call_count == 2

    document_repo.update_status.assert_any_call(
        "document-123",
        "ocr_complete",
    )

    document_repo.update_status.assert_any_call(
        "document-123",
        "extraction_complete",
    )


@pytest.mark.asyncio
async def test_process_pdf_rejects_non_pdf():
    (
        service,
        document_repo,
        ocr_repo,
        extraction_repo,
    ) = create_service()

    file = create_upload_file(
        filename="document.txt",
        content_type="text/plain",
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.process_pdf(file)

    assert exc_info.value.status_code == 415

    assert exc_info.value.detail == (
        "Only PDF files are supported."
    )

    document_repo.create.assert_not_called()

    service.ocr_service.process_pdf.assert_not_called()

    service.extraction_service.extract.assert_not_called()


@pytest.mark.asyncio
async def test_process_pdf_combines_ocr_page_text():
    (
        service,
        document_repo,
        ocr_repo,
        extraction_repo,
    ) = create_service()

    document = create_document()

    ocr_result = OCRResponse(
        filename="invoice.pdf",
        page_count=3,
        pages=[
            OCRPage(
                page_number=1,
                extracted_text="Page One",
                average_confidence=90.0,
            ),
            OCRPage(
                page_number=2,
                extracted_text="Page Two",
                average_confidence=80.0,
            ),
            OCRPage(
                page_number=3,
                extracted_text="Page Three",
                average_confidence=70.0,
            ),
        ],
        processing_time=2.0,
        status="success",
    )

    extraction_result = create_extraction_result()

    document_repo.create.return_value = document

    service.ocr_service.process_pdf = AsyncMock(
        return_value=ocr_result
    )

    service.extraction_service.extract.return_value = (
        extraction_result
    )

    file = create_upload_file()

    await service.process_pdf(file)

    expected_text = (
        "Page One\n\n"
        "Page Two\n\n"
        "Page Three"
    )

    service.extraction_service.extract.assert_called_once_with(
        document_text=expected_text,
        document_type="auto",
    )


@pytest.mark.asyncio
async def test_process_pdf_calculates_average_ocr_confidence():
    (
        service,
        document_repo,
        ocr_repo,
        extraction_repo,
    ) = create_service()

    document = create_document()

    ocr_result = OCRResponse(
        filename="invoice.pdf",
        page_count=3,
        pages=[
            OCRPage(
                page_number=1,
                extracted_text="One",
                average_confidence=90.0,
            ),
            OCRPage(
                page_number=2,
                extracted_text="Two",
                average_confidence=80.0,
            ),
            OCRPage(
                page_number=3,
                extracted_text="Three",
                average_confidence=70.0,
            ),
        ],
        processing_time=1.5,
        status="success",
    )

    document_repo.create.return_value = document

    service.ocr_service.process_pdf = AsyncMock(
        return_value=ocr_result
    )

    service.extraction_service.extract.return_value = (
        create_extraction_result()
    )

    file = create_upload_file()

    await service.process_pdf(file)

    ocr_repo.create.assert_called_once()

    call_kwargs = ocr_repo.create.call_args.kwargs

    assert call_kwargs["average_confidence"] == 80.0
    assert call_kwargs["page_count"] == 3
    assert call_kwargs["processing_time"] == 1.5


@pytest.mark.asyncio
async def test_process_pdf_handles_ocr_failure():
    (
        service,
        document_repo,
        ocr_repo,
        extraction_repo,
    ) = create_service()

    document = create_document()

    document_repo.create.return_value = document

    service.ocr_service.process_pdf = AsyncMock(
        side_effect=OCRException("OCR failed")
    )

    file = create_upload_file()

    with pytest.raises(PipelineOCRStageError):
        await service.process_pdf(file)

    document_repo.update_status.assert_called_once_with(
        "document-123",
        "failed",
    )

    ocr_repo.create.assert_not_called()

    extraction_repo.create.assert_not_called()

    service.extraction_service.extract.assert_not_called()


@pytest.mark.asyncio
async def test_process_pdf_handles_extraction_failure():
    (
        service,
        document_repo,
        ocr_repo,
        extraction_repo,
    ) = create_service()

    document = create_document()
    ocr_result = create_ocr_response()

    document_repo.create.return_value = document

    service.ocr_service.process_pdf = AsyncMock(
        return_value=ocr_result
    )

    service.extraction_service.extract.side_effect = (
        ExtractionException("Extraction failed")
    )

    file = create_upload_file()

    with pytest.raises(PipelineExtractionStageError):
        await service.process_pdf(file)

    document_repo.update_status.assert_any_call(
        "document-123",
        "ocr_complete",
    )

    document_repo.update_status.assert_any_call(
        "document-123",
        "failed",
    )

    ocr_repo.create.assert_called_once()

    extraction_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_process_pdf_passes_document_type_to_extraction():
    (
        service,
        document_repo,
        ocr_repo,
        extraction_repo,
    ) = create_service()

    document = create_document()
    ocr_result = create_ocr_response()

    document_repo.create.return_value = document

    service.ocr_service.process_pdf = AsyncMock(
        return_value=ocr_result
    )

    service.extraction_service.extract.return_value = (
        create_extraction_result()
    )

    file = create_upload_file()

    await service.process_pdf(
        file=file,
        document_type="contract",
    )

    service.extraction_service.extract.assert_called_once_with(
        document_text=(
            "Invoice Number INV-001\n\n"
            "Total Amount 1500"
        ),
        document_type="contract",
    )


@pytest.mark.asyncio
async def test_process_pdf_adds_document_id_to_result():
    (
        service,
        document_repo,
        ocr_repo,
        extraction_repo,
    ) = create_service()

    document = create_document()
    ocr_result = create_ocr_response()

    extraction_result = create_extraction_result()

    document_repo.create.return_value = document

    service.ocr_service.process_pdf = AsyncMock(
        return_value=ocr_result
    )

    service.extraction_service.extract.return_value = (
        extraction_result
    )

    file = create_upload_file()

    result = await service.process_pdf(file)

    assert result["document_id"] == "document-123"