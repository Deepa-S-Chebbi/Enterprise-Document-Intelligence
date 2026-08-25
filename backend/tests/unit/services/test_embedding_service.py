import math

import pytest

from app.services.embedding_service import EmbeddingService


@pytest.fixture(scope="module")
def embedding_service():
    return EmbeddingService()


def test_embed_text_returns_vector(embedding_service):
    vector = embedding_service.embed_text(
        "This is an enterprise invoice."
    )

    assert isinstance(vector, list)
    assert len(vector) > 0


def test_embed_text_returns_384_dimensions(embedding_service):
    vector = embedding_service.embed_text(
        "This is an enterprise invoice."
    )

    assert len(vector) == 384


def test_embed_text_contains_floats(embedding_service):
    vector = embedding_service.embed_text(
        "This is an enterprise invoice."
    )

    assert all(
        isinstance(value, float)
        for value in vector
    )


def test_embed_text_is_normalized(embedding_service):
    vector = embedding_service.embed_text(
        "This is an enterprise invoice."
    )

    magnitude = math.sqrt(
        sum(value * value for value in vector)
    )

    assert magnitude == pytest.approx(
        1.0,
        abs=1e-5,
    )


def test_same_text_produces_consistent_embedding(
    embedding_service,
):
    text = "Invoice total amount is 4500."

    vector_1 = embedding_service.embed_text(text)
    vector_2 = embedding_service.embed_text(text)

    assert vector_1 == pytest.approx(
        vector_2,
        abs=1e-6,
    )


def test_empty_text_raises_value_error(
    embedding_service,
):
    with pytest.raises(ValueError):
        embedding_service.embed_text("")


def test_whitespace_text_raises_value_error(
    embedding_service,
):
    with pytest.raises(ValueError):
        embedding_service.embed_text("   ")


def test_embed_texts_returns_multiple_vectors(
    embedding_service,
):
    texts = [
        "Invoice total is 4500.",
        "Payment is due within 30 days.",
        "Customer ABC placed an order.",
    ]

    vectors = embedding_service.embed_texts(texts)

    assert isinstance(vectors, list)
    assert len(vectors) == len(texts)


def test_embed_texts_returns_384_dimensions(
    embedding_service,
):
    texts = [
        "Invoice total is 4500.",
        "Payment is due within 30 days.",
    ]

    vectors = embedding_service.embed_texts(texts)

    for vector in vectors:
        assert len(vector) == 384


def test_embed_texts_empty_list_raises_value_error(
    embedding_service,
):
    with pytest.raises(ValueError):
        embedding_service.embed_texts([])


def test_embed_texts_rejects_empty_values(
    embedding_service,
):
    texts = [
        "Valid document text.",
        "",
        "Another valid document.",
    ]

    with pytest.raises(ValueError):
        embedding_service.embed_texts(texts)


def test_embed_texts_rejects_whitespace_values(
    embedding_service,
):
    texts = [
        "Valid document text.",
        "   ",
        "Another valid document.",
    ]

    with pytest.raises(ValueError):
        embedding_service.embed_texts(texts)