from unittest.mock import MagicMock, patch

import pytest

from app.services.extraction_service import ExtractionService


def test_extract_returns_parsed_response():
    document_text = "Invoice Number: INV-001"
    document_type = "invoice"

    expected_prompt = "EXTRACTION PROMPT"
    raw_llm_response = '{"document_type": "invoice"}'
    parsed_response = {
        "document_type": "invoice",
        "fields": [],
        "overall_confidence": 0.95,
    }

    with patch(
        "app.services.extraction_service.PromptBuilder.build_extraction_prompt"
    ) as mock_build_prompt, patch(
        "app.services.extraction_service.GeminiClient"
    ) as mock_gemini_client, patch(
        "app.services.extraction_service.ResponseParser.parse_json"
    ) as mock_parse_json:

        mock_build_prompt.return_value = expected_prompt

        mock_client = MagicMock()
        mock_client.generate.return_value = raw_llm_response
        mock_gemini_client.return_value = mock_client

        mock_parse_json.return_value = parsed_response

        service = ExtractionService()

        result = service.extract(
            document_text=document_text,
            document_type=document_type,
        )

    assert result == parsed_response

    mock_build_prompt.assert_called_once_with(
        document_text=document_text,
        document_type=document_type,
    )

    mock_gemini_client.assert_called_once_with()

    mock_client.generate.assert_called_once_with(
        expected_prompt
    )

    mock_parse_json.assert_called_once_with(
        raw_llm_response
    )


def test_extract_uses_auto_document_type_by_default():
    document_text = "Some document text"

    expected_prompt = "AUTO PROMPT"
    raw_llm_response = '{"document_type": "unknown"}'
    parsed_response = {
        "document_type": "unknown",
    }

    with patch(
        "app.services.extraction_service.PromptBuilder.build_extraction_prompt"
    ) as mock_build_prompt, patch(
        "app.services.extraction_service.GeminiClient"
    ) as mock_gemini_client, patch(
        "app.services.extraction_service.ResponseParser.parse_json"
    ) as mock_parse_json:

        mock_build_prompt.return_value = expected_prompt

        mock_client = MagicMock()
        mock_client.generate.return_value = raw_llm_response
        mock_gemini_client.return_value = mock_client

        mock_parse_json.return_value = parsed_response

        service = ExtractionService()

        result = service.extract(document_text)

    assert result == parsed_response

    mock_build_prompt.assert_called_once_with(
        document_text=document_text,
        document_type="auto",
    )


def test_extract_passes_raw_llm_response_to_parser():
    raw_llm_response = """
    {
        "document_type": "invoice",
        "fields": []
    }
    """

    parsed_response = {
        "document_type": "invoice",
        "fields": [],
    }

    with patch(
        "app.services.extraction_service.PromptBuilder.build_extraction_prompt"
    ) as mock_build_prompt, patch(
        "app.services.extraction_service.GeminiClient"
    ) as mock_gemini_client, patch(
        "app.services.extraction_service.ResponseParser.parse_json"
    ) as mock_parse_json:

        mock_build_prompt.return_value = "PROMPT"

        mock_client = MagicMock()
        mock_client.generate.return_value = raw_llm_response
        mock_gemini_client.return_value = mock_client

        mock_parse_json.return_value = parsed_response

        service = ExtractionService()

        result = service.extract(
            document_text="Invoice text",
            document_type="invoice",
        )

    assert result == parsed_response

    mock_parse_json.assert_called_once_with(
        raw_llm_response
    )


def test_extract_propagates_parser_error():
    from app.exceptions.extraction_exceptions import (
        MalformedExtractionResponseError,
    )

    with patch(
        "app.services.extraction_service.PromptBuilder.build_extraction_prompt"
    ) as mock_build_prompt, patch(
        "app.services.extraction_service.GeminiClient"
    ) as mock_gemini_client, patch(
        "app.services.extraction_service.ResponseParser.parse_json"
    ) as mock_parse_json:

        mock_build_prompt.return_value = "PROMPT"

        mock_client = MagicMock()
        mock_client.generate.return_value = '{"broken": true}'
        mock_gemini_client.return_value = mock_client

        mock_parse_json.side_effect = MalformedExtractionResponseError(
            "Invalid LLM response"
        )

        service = ExtractionService()

        with pytest.raises(MalformedExtractionResponseError):
            service.extract(
                document_text="Invoice text",
                document_type="invoice",
            )