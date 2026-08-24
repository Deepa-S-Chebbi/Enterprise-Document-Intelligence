from PIL import Image

from app.ocr.image_preprocessor import preprocess_image


def test_preprocess_image_returns_pil_image():
    image = Image.new("RGB", (100, 100), color="white")

    result = preprocess_image(image)

    assert isinstance(result, Image.Image)


def test_preprocess_image_preserves_dimensions():
    image = Image.new("RGB", (100, 100), color="white")

    result = preprocess_image(image)

    assert result.size == image.size


def test_preprocess_image_returns_grayscale_image():
    image = Image.new("RGB", (100, 100), color="white")

    result = preprocess_image(image)

    assert result.mode == "L"


def test_preprocess_image_converts_image_to_binary_values():
    image = Image.new("RGB", (100, 100), color="white")

    result = preprocess_image(image)

    unique_values = set(result.getdata())

    assert unique_values.issubset({0, 255})