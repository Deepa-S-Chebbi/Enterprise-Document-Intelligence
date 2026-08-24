import pytest

from app.exceptions.extraction_exceptions import (
    MalformedExtractionResponseError,
)
from app.llm.response_parser import ResponseParser


def test_parse_json_accepts_valid_json():
    response = '{"document_type": "invoice", "confidence": 0.95}'

    result = ResponseParser.parse_json(response)

    assert result == {
        "document_type": "invoice",
        "confidence": 0.95,
    }


def test_parse_json_removes_json_code_fences():
    response = """```json
{
    "document_type": "invoice",
    "confidence": 0.95
}
```"""

    result = ResponseParser.parse_json(response)

    assert result["document_type"] == "invoice"
    assert result["confidence"] == 0.95


def test_parse_json_removes_generic_code_fences():
    response = """```
{
    "document_type": "invoice"
}
```"""

    result = ResponseParser.parse_json(response)

    assert result["document_type"] == "invoice"


def test_parse_json_rejects_malformed_json():
    response = '{"document_type": "invoice",'

    with pytest.raises(MalformedExtractionResponseError):
        ResponseParser.parse_json(response)


@pytest.mark.parametrize(
    "response",
    [
        '["invoice", "resume"]',
        '"invoice"',
        '123',
        'true',
        'null',
    ],
)
def test_parse_json_rejects_non_object_json(response):
    with pytest.raises(MalformedExtractionResponseError):
        ResponseParser.parse_json(response)
