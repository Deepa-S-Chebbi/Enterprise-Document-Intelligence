from unittest.mock import Mock

import pytest

from app.services.semantic_retrieval_service import (
    SemanticRetrievalService,
)


def test_retrieve_generates_query_embedding():
    embedding_service = Mock()
    vector_store = Mock()

    embedding_service.embed_text.return_value = [
        0.1,
        0.2,
        0.3,
    ]

    vector_store.search.return_value = []

    service = SemanticRetrievalService(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    service.retrieve("What is the invoice total?")

    embedding_service.embed_text.assert_called_once_with(
        "What is the invoice total?"
    )


def test_retrieve_searches_vector_store():
    embedding_service = Mock()
    vector_store = Mock()

    embedding = [0.1, 0.2, 0.3]

    embedding_service.embed_text.return_value = embedding
    vector_store.search.return_value = ["result"]

    service = SemanticRetrievalService(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    results = service.retrieve(
        "What is the invoice total?",
        limit=3,
    )

    vector_store.search.assert_called_once_with(
        vector=embedding,
        limit=3,
    )

    assert results == ["result"]


def test_retrieve_uses_default_limit():
    embedding_service = Mock()
    vector_store = Mock()

    embedding_service.embed_text.return_value = [
        0.1,
        0.2,
        0.3,
    ]

    vector_store.search.return_value = []

    service = SemanticRetrievalService(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    service.retrieve("Find the invoice.")

    vector_store.search.assert_called_once_with(
        vector=[0.1, 0.2, 0.3],
        limit=5,
    )


def test_empty_query_raises_value_error():
    embedding_service = Mock()
    vector_store = Mock()

    service = SemanticRetrievalService(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    with pytest.raises(ValueError):
        service.retrieve("")


def test_whitespace_query_raises_value_error():
    embedding_service = Mock()
    vector_store = Mock()

    service = SemanticRetrievalService(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    with pytest.raises(ValueError):
        service.retrieve("   ")


def test_invalid_limit_raises_value_error():
    embedding_service = Mock()
    vector_store = Mock()

    service = SemanticRetrievalService(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    with pytest.raises(ValueError):
        service.retrieve(
            "Find the invoice.",
            limit=0,
        )


def test_negative_limit_raises_value_error():
    embedding_service = Mock()
    vector_store = Mock()

    service = SemanticRetrievalService(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    with pytest.raises(ValueError):
        service.retrieve(
            "Find the invoice.",
            limit=-1,
        )


def test_retrieve_returns_multiple_results():
    embedding_service = Mock()
    vector_store = Mock()

    embedding_service.embed_text.return_value = [
        0.1,
        0.2,
        0.3,
    ]

    expected_results = [
        "chunk one",
        "chunk two",
        "chunk three",
    ]

    vector_store.search.return_value = expected_results

    service = SemanticRetrievalService(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    results = service.retrieve(
        "Tell me about the document.",
        limit=3,
    )

    assert results == expected_results