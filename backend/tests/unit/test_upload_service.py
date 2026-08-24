from io import BytesIO
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import UploadFile

from app.exceptions.upload_exceptions import (
    FileTooLargeError,
    InvalidFileTypeError,
)
from app.services.upload_service import UploadService


def create_upload_file(
    filename: str = "invoice.pdf",
    content: bytes = b"test content",
    content_type: str = "application/pdf",
) -> UploadFile:
    file = UploadFile(
        filename=filename,
        file=BytesIO(content),
    )

    file.headers = {
        "content-type": content_type,
    }

    # UploadFile.size is normally populated by FastAPI/Starlette
    file.size = len(content)

    return file


@pytest.mark.asyncio
@patch("app.services.upload_service.generate_unique_filename")
@patch(
    "app.services.upload_service.validate_file_size",
    new_callable=AsyncMock,
)
@patch("app.services.upload_service.validate_file_type")
async def test_upload_file_success(
    mock_validate_type,
    mock_validate_size,
    mock_generate_filename,
):
    mock_generate_filename.return_value = (
        "doc-123",
        "doc-123.pdf",
    )

    service = UploadService()
    service.storage.save_file = AsyncMock()

    file = create_upload_file()

    response = await service.upload_file(file)

    assert response.document_id == "doc-123"
    assert response.filename == "doc-123.pdf"
    assert response.original_filename == "invoice.pdf"
    assert response.content_type == "application/pdf"
    assert response.file_size == len(b"test content")
    assert response.status == "uploaded"

    mock_validate_type.assert_called_once_with(file)
    mock_validate_size.assert_awaited_once_with(file)
    mock_generate_filename.assert_called_once_with("invoice.pdf")

    service.storage.save_file.assert_awaited_once_with(
        file=file,
        filename="doc-123.pdf",
    )


@pytest.mark.asyncio
@patch("app.services.upload_service.validate_file_type")
async def test_upload_file_rejects_invalid_file_type(
    mock_validate_type,
):
    mock_validate_type.side_effect = InvalidFileTypeError(
        "Unsupported file type"
    )

    service = UploadService()
    service.storage.save_file = AsyncMock()

    file = create_upload_file(
        filename="malware.exe",
    )

    with pytest.raises(InvalidFileTypeError):
        await service.upload_file(file)

    service.storage.save_file.assert_not_awaited()


@pytest.mark.asyncio
@patch(
    "app.services.upload_service.validate_file_size",
    new_callable=AsyncMock,
)
async def test_upload_file_rejects_large_file(
    mock_validate_size,
):
    mock_validate_size.side_effect = FileTooLargeError(
        "File is too large"
    )

    service = UploadService()
    service.storage.save_file = AsyncMock()

    file = create_upload_file()

    with pytest.raises(FileTooLargeError):
        await service.upload_file(file)

    service.storage.save_file.assert_not_awaited()


@pytest.mark.asyncio
@patch("app.services.upload_service.generate_unique_filename")
@patch(
    "app.services.upload_service.validate_file_size",
    new_callable=AsyncMock,
)
@patch("app.services.upload_service.validate_file_type")
async def test_upload_file_uses_generated_filename(
    mock_validate_type,
    mock_validate_size,
    mock_generate_filename,
):
    mock_generate_filename.return_value = (
        "unique-id",
        "unique-id.pdf",
    )

    service = UploadService()
    service.storage.save_file = AsyncMock()

    file = create_upload_file()

    await service.upload_file(file)

    service.storage.save_file.assert_awaited_once_with(
        file=file,
        filename="unique-id.pdf",
    )