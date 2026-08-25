from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import settings


def test_upload_pdf_success(client: TestClient):
    response = client.post(
        "/api/v1/upload",
        files={
            "file": (
                "invoice.pdf",
                BytesIO(b"%PDF-1.4 fake pdf content"),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["original_filename"] == "invoice.pdf"
    assert data["content_type"] == "application/pdf"
    assert data["status"] == "uploaded"

    assert data["document_id"]
    assert data["filename"]
    assert data["file_size"] > 0
    assert data["upload_time"]

    # Clean up the file created by the integration test.
    uploaded_file = (
        Path(settings.upload_directory)
        / data["filename"]
    )

    if uploaded_file.exists():
        uploaded_file.unlink()