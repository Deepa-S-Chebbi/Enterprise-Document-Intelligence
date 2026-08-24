from unittest.mock import patch

import pytesseract
from PIL import Image

from app.core.config import settings
from app.ocr.tesseract_engine import extract_text


def create_test_image():
    return Image.new("RGB", (100, 100), color="white")


@patch("app.ocr.tesseract_engine.pytesseract.image_to_data")
def test_extract_text_returns_text_and_average_confidence(mock_ocr):
    mock_ocr.return_value = {
        "text": ["Invoice", "Number", "INV-001"],
        "conf": ["95", "90", "85"],
    }

    image = create_test_image()

    text, confidence = extract_text(image)

    assert text == "Invoice Number INV-001"
    assert confidence == 90.0


@patch("app.ocr.tesseract_engine.pytesseract.image_to_data")
def test_extract_text_ignores_empty_text(mock_ocr):
    mock_ocr.return_value = {
        "text": ["Invoice", "", "INV-001"],
        "conf": ["95", "80", "85"],
    }

    image = create_test_image()

    text, confidence = extract_text(image)

    assert text == "Invoice INV-001"
    assert confidence == 90.0


@patch("app.ocr.tesseract_engine.pytesseract.image_to_data")
def test_extract_text_ignores_negative_confidence(mock_ocr):
    mock_ocr.return_value = {
        "text": ["Invoice", "Number", "Unknown"],
        "conf": ["95", "-1", "85"],
    }

    image = create_test_image()

    text, confidence = extract_text(image)

    assert text == "Invoice Number Unknown"
    assert confidence == 90.0


@patch("app.ocr.tesseract_engine.pytesseract.image_to_data")
def test_extract_text_ignores_invalid_confidence(mock_ocr):
    mock_ocr.return_value = {
        "text": ["Invoice", "Number"],
        "conf": ["95", "invalid"],
    }

    image = create_test_image()

    text, confidence = extract_text(image)

    assert text == "Invoice Number"
    assert confidence == 95.0


@patch("app.ocr.tesseract_engine.pytesseract.image_to_data")
def test_extract_text_returns_zero_confidence_when_none_are_valid(mock_ocr):
    mock_ocr.return_value = {
        "text": ["Unknown"],
        "conf": ["-1"],
    }

    image = create_test_image()

    text, confidence = extract_text(image)

    assert text == "Unknown"
    assert confidence == 0.0


@patch("app.ocr.tesseract_engine.pytesseract.image_to_data")
def test_extract_text_calls_tesseract_with_correct_settings(mock_ocr):
    mock_ocr.return_value = {
        "text": [],
        "conf": [],
    }

    image = create_test_image()

    extract_text(image)

    mock_ocr.assert_called_once()

    call_args = mock_ocr.call_args

    assert call_args.args[0] is image
    assert call_args.kwargs["lang"] == settings.ocr_language
    assert call_args.kwargs["output_type"] == pytesseract.Output.DICT