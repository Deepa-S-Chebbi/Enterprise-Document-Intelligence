from unittest.mock import Mock

import pytest

from app.services.rag_qa_service import RAGQAService


def test_answer_retrieves_context_and_generates_answer():
    retrieval_service = Mock()
    generation_service = Mock()

    retrieval_service.retrieve.return_value = [
        "The invoice total is 4500.",
        "Payment is due within 30 days.",
    ]

    generation_service.generate_answer.return_value = (
        "The invoice total is 4500."
    )

    service = RAGQAService(
        retrieval_service=retrieval_service,
        generation_service=generation_service,
    )

    result = service.answer(
        query="What is the invoice total?",
        limit=3,
    )

    assert result == "The invoice total is 4500."

    retrieval_service.retrieve.assert_called_once_with(
        query="What is the invoice total?",
        limit=3,
    )

    generation_service.generate_answer.assert_called_once_with(
        query="What is the invoice total?",
        context=[
            "The invoice total is 4500.",
            "Payment is due within 30 days.",
        ],
    )


def test_answer_extracts_text_from_qdrant_results():
    retrieval_service = Mock()
    generation_service = Mock()

    result_one = Mock()
    result_one.payload = {
        "document_id": "doc-1",
        "text": "Invoice total is 4500.",
    }

    result_two = Mock()
    result_two.payload = {
        "document_id": "doc-1",
        "text": "Payment is due within 30 days.",
    }

    retrieval_service.retrieve.return_value = [
        result_one,
        result_two,
    ]

    generation_service.generate_answer.return_value = (
        "The invoice total is 4500."
    )

    service = RAGQAService(
        retrieval_service=retrieval_service,
        generation_service=generation_service,
    )

    result = service.answer(
        "What is the invoice total?"
    )

    assert result == "The invoice total is 4500."

    generation_service.generate_answer.assert_called_once_with(
        query="What is the invoice total?",
        context=[
            "Invoice total is 4500.",
            "Payment is due within 30 days.",
        ],
    )


def test_answer_uses_default_limit():
    retrieval_service = Mock()
    generation_service = Mock()

    retrieval_service.retrieve.return_value = [
        "Some document content."
    ]

    generation_service.generate_answer.return_value = "Answer."

    service = RAGQAService(
        retrieval_service=retrieval_service,
        generation_service=generation_service,
    )

    service.answer("What is this document about?")

    retrieval_service.retrieve.assert_called_once_with(
        query="What is this document about?",
        limit=5,
    )


def test_answer_rejects_empty_query():
    retrieval_service = Mock()
    generation_service = Mock()

    service = RAGQAService(
        retrieval_service=retrieval_service,
        generation_service=generation_service,
    )

    with pytest.raises(ValueError):
        service.answer("")


def test_answer_rejects_whitespace_query():
    retrieval_service = Mock()
    generation_service = Mock()

    service = RAGQAService(
        retrieval_service=retrieval_service,
        generation_service=generation_service,
    )

    with pytest.raises(ValueError):
        service.answer("   ")


def test_answer_rejects_invalid_limit():
    retrieval_service = Mock()
    generation_service = Mock()

    service = RAGQAService(
        retrieval_service=retrieval_service,
        generation_service=generation_service,
    )

    with pytest.raises(ValueError):
        service.answer(
            "What is the invoice total?",
            limit=0,
        )


def test_answer_rejects_negative_limit():
    retrieval_service = Mock()
    generation_service = Mock()

    service = RAGQAService(
        retrieval_service=retrieval_service,
        generation_service=generation_service,
    )

    with pytest.raises(ValueError):
        service.answer(
            "What is the invoice total?",
            limit=-1,
        )


def test_answer_returns_fallback_when_no_results():
    retrieval_service = Mock()
    generation_service = Mock()

    retrieval_service.retrieve.return_value = []

    service = RAGQAService(
        retrieval_service=retrieval_service,
        generation_service=generation_service,
    )

    result = service.answer(
        "What is the invoice total?"
    )

    assert result == (
        "I could not find relevant information "
        "in the provided documents."
    )

    generation_service.generate_answer.assert_not_called()


def test_answer_skips_results_without_text():
    retrieval_service = Mock()
    generation_service = Mock()

    valid_result = Mock()
    valid_result.payload = {
        "text": "Invoice total is 4500."
    }

    empty_result = Mock()
    empty_result.payload = {}

    retrieval_service.retrieve.return_value = [
        empty_result,
        valid_result,
    ]

    generation_service.generate_answer.return_value = (
        "The invoice total is 4500."
    )

    result = service = RAGQAService(
        retrieval_service=retrieval_service,
        generation_service=generation_service,
    ).answer(
        "What is the invoice total?"
    )

    assert result == "The invoice total is 4500."