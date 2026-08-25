from uuid import uuid4

from fastapi.testclient import TestClient

from app.db.models.document import Document
from app.db.models.extraction_result import ExtractionResult
from app.db.models.ocr_result import OCRResult


def test_list_documents_returns_documents(
    client: TestClient,
    db_session,
):
    document = Document(
        original_filename="test-invoice.pdf",
        content_type="application/pdf",
        file_size=1024,
        status="uploaded",
    )

    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)

    response = client.get("/api/v1/documents")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1

    returned_document = next(
        item
        for item in data
        if item["id"] == str(document.id)
    )

    assert returned_document["original_filename"] == (
        "test-invoice.pdf"
    )
    assert returned_document["content_type"] == (
        "application/pdf"
    )
    assert returned_document["file_size"] == 1024
    assert returned_document["status"] == "uploaded"


def test_list_documents_supports_pagination(
    client: TestClient,
    db_session,
):
    documents = [
        Document(
            original_filename=f"document-{index}.pdf",
            content_type="application/pdf",
            file_size=1000 + index,
            status="uploaded",
        )
        for index in range(3)
    ]

    db_session.add_all(documents)
    db_session.commit()

    response = client.get(
        "/api/v1/documents",
        params={
            "skip": 1,
            "limit": 1,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1


def test_get_document_returns_complete_data(
    client: TestClient,
    db_session,
):
    document = Document(
        original_filename="invoice-001.pdf",
        content_type="application/pdf",
        file_size=2048,
        status="extraction_complete",
    )

    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)

    ocr_result = OCRResult(
        document_id=document.id,
        page_count=2,
        full_text="Invoice Number: INV-001\nTotal: 1500",
        average_confidence=94.5,
        processing_time=0.45,
    )

    extraction_result = ExtractionResult(
        document_id=document.id,
        document_type="invoice",
        fields={
            "invoice_number": "INV-001",
            "total": 1500,
        },
        overall_confidence=0.94,
        requires_review=False,
    )

    db_session.add(ocr_result)
    db_session.add(extraction_result)
    db_session.commit()

    response = client.get(
        f"/api/v1/documents/{document.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["document"]["id"] == str(document.id)
    assert data["document"]["original_filename"] == (
        "invoice-001.pdf"
    )
    assert data["document"]["status"] == (
        "extraction_complete"
    )

    assert data["ocr"]["page_count"] == 2
    assert data["ocr"]["full_text"] == (
        "Invoice Number: INV-001\nTotal: 1500"
    )
    assert data["ocr"]["average_confidence"] == 94.5

    assert data["extraction"]["document_type"] == "invoice"
    assert data["extraction"]["fields"]["invoice_number"] == (
        "INV-001"
    )
    assert data["extraction"]["fields"]["total"] == 1500
    assert data["extraction"]["overall_confidence"] == 0.94
    assert data["extraction"]["requires_review"] is False


def test_get_document_returns_404_when_not_found(
    client: TestClient,
):
    document_id = uuid4()

    response = client.get(
        f"/api/v1/documents/{document_id}"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Document not found"
    }