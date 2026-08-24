import pytest
from fastapi import UploadFile
from io import BytesIO

from app.utils.file_validation import (
    validate_file_type,
    validate_file_size,
)
from app.exceptions.upload_exceptions import (
    InvalidFileTypeError,
    FileTooLargeError,
)
from app.core.config import settings


def create_upload_file(filename: str, content: bytes) -> UploadFile:
    return UploadFile(
        filename=filename,
        file=BytesIO(content),
    )


def test_validate_file_type_accepts_pdf():
    file = create_upload_file(
        filename="document.pdf",
        content=b"test content",
    )

    validate_file_type(file)


def test_validate_file_type_rejects_unsupported_file():
    file = create_upload_file(
        filename="document.exe",
        content=b"test content",
    )

    with pytest.raises(InvalidFileTypeError):
        validate_file_type(file)


def test_validate_file_type_accepts_uppercase_extension():
    file = create_upload_file(
        filename="document.PDF",
        content=b"test content",
    )

    validate_file_type(file)


@pytest.mark.asyncio
async def test_validate_file_size_accepts_small_file():
    file = create_upload_file(
        filename="document.pdf",
        content=b"small file",
    )

    await validate_file_size(file)


@pytest.mark.asyncio
async def test_validate_file_size_rejects_large_file():
    large_content = b"x" * (settings.max_upload_size + 1)

    file = create_upload_file(
        filename="document.pdf",
        content=large_content,
    )

    with pytest.raises(FileTooLargeError):
        await validate_file_size(file)


@pytest.mark.asyncio
async def test_validate_file_size_resets_file_pointer():
    file = create_upload_file(
        filename="document.pdf",
        content=b"test content",
    )

    await validate_file_size(file)

    assert file.file.tell() == 0