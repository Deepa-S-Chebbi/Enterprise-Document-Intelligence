from pathlib import Path
from unittest.mock import patch

from PIL import Image

from app.ocr.pdf_converter import pdf_to_images
from app.core.config import settings


@patch("app.ocr.pdf_converter.convert_from_path")
def test_pdf_to_images_returns_converted_images(mock_convert):
    fake_images = [
        Image.new("RGB", (100, 100)),
        Image.new("RGB", (100, 100)),
    ]

    mock_convert.return_value = fake_images

    result = pdf_to_images("sample.pdf")

    assert result == fake_images
    assert len(result) == 2


@patch("app.ocr.pdf_converter.convert_from_path")
def test_pdf_to_images_passes_correct_settings(mock_convert):
    mock_convert.return_value = []

    pdf_to_images("sample.pdf")

    mock_convert.assert_called_once_with(
        Path("sample.pdf"),
        dpi=settings.pdf_dpi,
        poppler_path=settings.poppler_path,
    )