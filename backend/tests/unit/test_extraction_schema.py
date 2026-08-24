import pytest
from pydantic import ValidationError

from app.schemas.extraction import (
    DocumentField,
    ExtractionResponse,
    ExtractionRequest,
)


def test_document_field_accepts_valid_data():
    field = DocumentField(
        field_name="invoice_number",
        value="INV-001",
        confidence=0.95,
        source_text="Invoice Number: INV-001",
    )

    assert field.field_name == "invoice_number"
    assert field.value == "INV-001"
    assert field.confidence == 0.95


@pytest.mark.parametrize("confidence", [-0.1, 1.1])
def test_document_field_rejects_invalid_confidence(confidence):
    with pytest.raises(ValidationError):
        DocumentField(
            field_name="invoice_number",
            value="INV-001",
            confidence=confidence,
        )


def test_extraction_response_accepts_valid_data():
    response = ExtractionResponse(
        document_type="invoice",
        fields=[
            DocumentField(
                field_name="invoice_number",
                value="INV-001",
                confidence=0.95,
            )
        ],
        overall_confidence=0.92,
        processing_time=1.5,
        requires_review=False,
        status="success",
        document_id="doc-123",
    )

    assert response.document_type == "invoice"
    assert response.status == "success"
    assert response.requires_review is False


def test_extraction_response_rejects_invalid_document_type():
    with pytest.raises(ValidationError):
        ExtractionResponse(
            document_type="passport",
            fields=[],
            overall_confidence=0.8,
            processing_time=1.0,
            requires_review=False,
            status="success",
        )


def test_extraction_response_rejects_invalid_status():
    with pytest.raises(ValidationError):
        ExtractionResponse(
            document_type="invoice",
            fields=[],
            overall_confidence=0.8,
            processing_time=1.0,
            requires_review=False,
            status="pending",
        )


def test_extraction_request_defaults_to_auto():
    request = ExtractionRequest(
        document_text="Invoice Number: INV-001"
    )

    assert request.document_type == "auto"


def test_extraction_request_accepts_valid_document_type():
    request = ExtractionRequest(
        document_text="Invoice Number: INV-001",
        document_type="invoice",
    )

    assert request.document_type == "invoice"