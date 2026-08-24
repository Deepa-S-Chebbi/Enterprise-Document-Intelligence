from io import BytesIO
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import UploadFile
from PIL import Image

from app.exceptions.ocr_exceptions import OCRProcessingError
from app.services.ocr_service import OCRService


def create_upload_file(
    filename: str = "invoice.pdf",
) -> UploadFile:
    return UploadFile(
        filename=filename,
        file=BytesIO(b"fake pdf content"),
    )


@pytest.mark.asyncio
@patch("app.services.ocr_service.extract_text")
@patch("app.services.ocr_service.preprocess_image")
@patch("app.services.ocr_service.pdf_to_images")
@patch("app.services.ocr_service.generate_unique_filename")
async def test_process_pdf_success(
    mock_generate_filename,
    mock_pdf_to_images,
    mock_preprocess_image,
    mock_extract_text,
):
    mock_generate_filename.return_value = (
        "doc-123",
        "doc-123.pdf",
    )

    fake_images = [
        Image.new("RGB", (100, 100)),
    ]

    mock_pdf_to_images.return_value = fake_images
    mock_preprocess_image.return_value = fake_images[0]
    mock_extract_text.return_value = (
        "Invoice Number INV-001",
        95.0,
    )

    service = OCRService()

    service.storage.save_file = AsyncMock(
        return_value=Path("uploads/doc-123.pdf")
    )

    service.storage.delete_file = MagicMock()

    file = create_upload_file()

    response = await service.process_pdf(file)

    assert response.filename == "invoice.pdf"
    assert response.page_count == 1
    assert response.status == "success"

    assert len(response.pages) == 1
    assert response.pages[0].page_number == 1
    assert response.pages[0].extracted_text == (
        "Invoice Number INV-001"
    )
    assert response.pages[0].average_confidence == 95.0

    mock_generate_filename.assert_called_once_with(
        "invoice.pdf"
    )

    service.storage.save_file.assert_awaited_once_with(
        file=file,
        filename="doc-123.pdf",
    )

    mock_pdf_to_images.assert_called_once_with(
        str(Path("uploads/doc-123.pdf"))
    )

    mock_preprocess_image.assert_called_once_with(
        fake_images[0]
    )

    mock_extract_text.assert_called_once_with(
        fake_images[0]
    )

    service.storage.delete_file.assert_called_once_with(
        Path("uploads/doc-123.pdf")
    )


@pytest.mark.asyncio
@patch("app.services.ocr_service.extract_text")
@patch("app.services.ocr_service.preprocess_image")
@patch("app.services.ocr_service.pdf_to_images")
@patch("app.services.ocr_service.generate_unique_filename")
async def test_process_pdf_handles_multiple_pages(
    mock_generate_filename,
    mock_pdf_to_images,
    mock_preprocess_image,
    mock_extract_text,
):
    mock_generate_filename.return_value = (
        "doc-456",
        "doc-456.pdf",
    )

    fake_images = [
        Image.new("RGB", (100, 100)),
        Image.new("RGB", (100, 100)),
        Image.new("RGB", (100, 100)),
    ]

    mock_pdf_to_images.return_value = fake_images
    mock_preprocess_image.side_effect = fake_images

    mock_extract_text.side_effect = [
        ("Page one text", 90.0),
        ("Page two text", 85.0),
        ("Page three text", 95.0),
    ]

    service = OCRService()

    service.storage.save_file = AsyncMock(
        return_value=Path("uploads/doc-456.pdf")
    )

    service.storage.delete_file = MagicMock()

    file = create_upload_file()

    response = await service.process_pdf(file)

    assert response.page_count == 3
    assert len(response.pages) == 3

    assert response.pages[0].page_number == 1
    assert response.pages[0].extracted_text == "Page one text"
    assert response.pages[0].average_confidence == 90.0

    assert response.pages[1].page_number == 2
    assert response.pages[1].extracted_text == "Page two text"
    assert response.pages[1].average_confidence == 85.0

    assert response.pages[2].page_number == 3
    assert response.pages[2].extracted_text == "Page three text"
    assert response.pages[2].average_confidence == 95.0

    assert mock_preprocess_image.call_count == 3
    assert mock_extract_text.call_count == 3

    service.storage.delete_file.assert_called_once_with(
        Path("uploads/doc-456.pdf")
    )


@pytest.mark.asyncio
@patch("app.services.ocr_service.pdf_to_images")
@patch("app.services.ocr_service.generate_unique_filename")
async def test_process_pdf_converts_processing_errors(
    mock_generate_filename,
    mock_pdf_to_images,
):
    mock_generate_filename.return_value = (
        "doc-789",
        "doc-789.pdf",
    )

    mock_pdf_to_images.side_effect = RuntimeError(
        "PDF conversion failed"
    )

    service = OCRService()

    service.storage.save_file = AsyncMock(
        return_value=Path("uploads/doc-789.pdf")
    )

    service.storage.delete_file = MagicMock()

    file = create_upload_file()

    with pytest.raises(OCRProcessingError):
        await service.process_pdf(file)

    service.storage.delete_file.assert_called_once_with(
        Path("uploads/doc-789.pdf")
    )


@pytest.mark.asyncio
@patch("app.services.ocr_service.extract_text")
@patch("app.services.ocr_service.preprocess_image")
@patch("app.services.ocr_service.pdf_to_images")
@patch("app.services.ocr_service.generate_unique_filename")
async def test_process_pdf_deletes_file_when_ocr_fails(
    mock_generate_filename,
    mock_pdf_to_images,
    mock_preprocess_image,
    mock_extract_text,
):
    mock_generate_filename.return_value = (
        "doc-error",
        "doc-error.pdf",
    )

    fake_image = Image.new("RGB", (100, 100))

    mock_pdf_to_images.return_value = [fake_image]
    mock_preprocess_image.return_value = fake_image

    mock_extract_text.side_effect = RuntimeError(
        "Tesseract failed"
    )

    service = OCRService()

    service.storage.save_file = AsyncMock(
        return_value=Path("uploads/doc-error.pdf")
    )

    service.storage.delete_file = MagicMock()

    file = create_upload_file()

    with pytest.raises(OCRProcessingError):
        await service.process_pdf(file)

    service.storage.delete_file.assert_called_once_with(
        Path("uploads/doc-error.pdf")
    )


@pytest.mark.asyncio
@patch("app.services.ocr_service.extract_text")
@patch("app.services.ocr_service.preprocess_image")
@patch("app.services.ocr_service.pdf_to_images")
@patch("app.services.ocr_service.generate_unique_filename")
async def test_process_pdf_assigns_correct_page_numbers(
    mock_generate_filename,
    mock_pdf_to_images,
    mock_preprocess_image,
    mock_extract_text,
):
    mock_generate_filename.return_value = (
        "doc-pages",
        "doc-pages.pdf",
    )

    fake_images = [
        Image.new("RGB", (100, 100)),
        Image.new("RGB", (100, 100)),
    ]

    mock_pdf_to_images.return_value = fake_images
    mock_preprocess_image.side_effect = fake_images

    mock_extract_text.side_effect = [
        ("First page", 91.0),
        ("Second page", 92.0),
    ]

    service = OCRService()

    service.storage.save_file = AsyncMock(
        return_value=Path("uploads/doc-pages.pdf")
    )

    service.storage.delete_file = MagicMock()

    file = create_upload_file()

    response = await service.process_pdf(file)

    assert [page.page_number for page in response.pages] == [1, 2]