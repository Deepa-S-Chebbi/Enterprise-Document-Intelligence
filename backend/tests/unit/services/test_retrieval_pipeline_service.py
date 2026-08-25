from unittest.mock import Mock

import pytest

from app.services.retrieval_pipeline_service import (
    RetrievalPipelineService,
)


def test_retrieve_returns_semantic_results():
    semantic_retrieval = Mock()

    expected_results = [
        {
            "document_id": "doc-1",
            "text": "Invoice total is 4500.",
            "score": 0.91,
        },
        {
            "document_id": "doc-1",
            "text": "Payment is due within 30 days.",
            "score": 0.84,
        },
    ]

    semantic_retrieval.retrieve.return_value = expected_results

    service = RetrievalPipelineService(
        semantic_retrieval_service=semantic_retrieval,
    )

    results = service.retrieve(
        query="What is the invoice total?",
        limit=2,
    )

    semantic_retrieval.retrieve.assert_called_once_with(
        "What is the invoice total?",
        limit=2,
    )

    assert results == expected_results


def test_retrieve_uses_default_limit():
    semantic_retrieval = Mock()
    semantic_retrieval.retrieve.return_value = []

    service = RetrievalPipelineService(
        semantic_retrieval_service=semantic_retrieval,
    )

    service.retrieve("Find the invoice.")

    semantic_retrieval.retrieve.assert_called_once_with(
        "Find the invoice.",
        limit=5,
    )


def test_empty_query_raises_value_error():
    semantic_retrieval = Mock()

    service = RetrievalPipelineService(
        semantic_retrieval_service=semantic_retrieval,
    )

    with pytest.raises(ValueError):
        service.retrieve("")


def test_whitespace_query_raises_value_error():
    semantic_retrieval = Mock()

    service = RetrievalPipelineService(
        semantic_retrieval_service=semantic_retrieval,
    )

    with pytest.raises(ValueError):
        service.retrieve("   ")


def test_invalid_limit_raises_value_error():
    semantic_retrieval = Mock()

    service = RetrievalPipelineService(
        semantic_retrieval_service=semantic_retrieval,
    )

    with pytest.raises(ValueError):
        service.retrieve(
            "Find the invoice.",
            limit=0,
        )


def test_negative_limit_raises_value_error():
    semantic_retrieval = Mock()

    service = RetrievalPipelineService(
        semantic_retrieval_service=semantic_retrieval,
    )

    with pytest.raises(ValueError):
        service.retrieve(
            "Find the invoice.",
            limit=-1,
        )