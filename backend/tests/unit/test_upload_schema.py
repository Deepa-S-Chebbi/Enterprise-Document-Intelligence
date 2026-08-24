from datetime import datetime, timezone

from app.schemas.upload import UploadResponse


def test_upload_response_accepts_valid_data():
    upload_time = datetime.now(timezone.utc)

    response = UploadResponse(
        document_id="doc-123",
        filename="generated-file.pdf",
        original_filename="invoice.pdf",
        content_type="application/pdf",
        file_size=2048,
        upload_time=upload_time,
        status="uploaded",
    )

    assert response.document_id == "doc-123"
    assert response.filename == "generated-file.pdf"
    assert response.original_filename == "invoice.pdf"
    assert response.content_type == "application/pdf"
    assert response.file_size == 2048
    assert response.upload_time == upload_time
    assert response.status == "uploaded"


def test_upload_response_preserves_file_size():
    response = UploadResponse(
        document_id="doc-456",
        filename="document.pdf",
        original_filename="document.pdf",
        content_type="application/pdf",
        file_size=5000,
        upload_time=datetime.now(timezone.utc),
        status="uploaded",
    )

    assert response.file_size == 5000