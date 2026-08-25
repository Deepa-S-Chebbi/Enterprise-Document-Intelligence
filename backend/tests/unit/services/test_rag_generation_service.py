from unittest.mock import Mock

import pytest

from app.services.rag_generation_service import (
    RAGGenerationService,
)


def test_generate_answer_sends_query_and_context_to_llm():
    llm_client = Mock()

    llm_client.generate.return_value = (
        "The invoice total is 4500."
    )

    service = RAGGenerationService(
        llm_client=llm_client,
    )

    result = service.generate_answer(
        query="What is the invoice total?",
        context=[
            "The total invoice amount is 4500.",
            "Payment is due within 30 days.",
        ],
    )

    assert result == "The invoice total is 4500."

    llm_client.generate.assert_called_once()

    prompt = llm_client.generate.call_args[0][0]

    assert "What is the invoice total?" in prompt
    assert "The total invoice amount is 4500." in prompt
    assert "Payment is due within 30 days." in prompt


def test_generate_answer_rejects_empty_query():
    llm_client = Mock()

    service = RAGGenerationService(
        llm_client=llm_client,
    )

    with pytest.raises(ValueError):
        service.generate_answer(
            query="",
            context=["Some document text."],
        )


def test_generate_answer_rejects_whitespace_query():
    llm_client = Mock()

    service = RAGGenerationService(
        llm_client=llm_client,
    )

    with pytest.raises(ValueError):
        service.generate_answer(
            query="   ",
            context=["Some document text."],
        )


def test_generate_answer_rejects_empty_context():
    llm_client = Mock()

    service = RAGGenerationService(
        llm_client=llm_client,
    )

    with pytest.raises(ValueError):
        service.generate_answer(
            query="What is this document about?",
            context=[],
        )


def test_generate_answer_rejects_whitespace_context():
    llm_client = Mock()

    service = RAGGenerationService(
        llm_client=llm_client,
    )

    with pytest.raises(ValueError):
        service.generate_answer(
            query="What is this document about?",
            context=["   ", ""],
        )


def test_generate_answer_ignores_empty_context_items():
    llm_client = Mock()

    llm_client.generate.return_value = "Answer."

    service = RAGGenerationService(
        llm_client=llm_client,
    )

    service.generate_answer(
        query="What is the answer?",
        context=[
            "Useful document content.",
            "",
            "   ",
        ],
    )

    prompt = llm_client.generate.call_args[0][0]

    assert "Useful document content." in prompt
    assert "[Document Context 1]" in prompt