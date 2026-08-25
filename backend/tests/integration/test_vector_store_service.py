from uuid import uuid4

import pytest
from qdrant_client.models import (
    FieldCondition,
    Filter,
    MatchValue,
)

from app.services.vector_store_service import VectorStoreService


@pytest.fixture
def vector_store():
    service = VectorStoreService()
    service.ensure_collection()
    return service


def test_ensure_collection_creates_document_chunks_collection(
    vector_store,
):
    collections = vector_store.client.get_collections()

    collection_names = {
        collection.name
        for collection in collections.collections
    }

    assert vector_store.COLLECTION_NAME in collection_names


def test_add_vector_stores_vector_and_payload(
    vector_store,
):
    point_id = str(uuid4())
    document_id = f"test-vector-{uuid4()}"

    vector = [0.1] * vector_store.VECTOR_SIZE

    payload = {
        "document_id": document_id,
        "text": "Test enterprise document.",
    }

    vector_store.add_vector(
        point_id=point_id,
        vector=vector,
        payload=payload,
    )

    results = vector_store.client.retrieve(
        collection_name=vector_store.COLLECTION_NAME,
        ids=[point_id],
        with_payload=True,
        with_vectors=True,
    )

    assert len(results) == 1

    stored = results[0]

    assert stored.payload["document_id"] == document_id
    assert stored.payload["text"] == "Test enterprise document."

    assert stored.vector is not None
    assert len(stored.vector) == vector_store.VECTOR_SIZE

    vector_store.delete_document(document_id)


def test_search_returns_similar_vectors(
    vector_store,
):
    document_id = f"test-search-{uuid4()}"
    point_id = str(uuid4())

    vector = [0.1] * vector_store.VECTOR_SIZE

    payload = {
        "document_id": document_id,
        "text": "Enterprise invoice total is 4500.",
    }

    vector_store.add_vector(
        point_id=point_id,
        vector=vector,
        payload=payload,
    )

    results = vector_store.search(
        vector=vector,
        limit=5,
    )

    matching_results = [
        result
        for result in results
        if result.payload
        and result.payload.get("document_id") == document_id
    ]

    assert matching_results

    result = matching_results[0]

    assert result.payload["text"] == (
        "Enterprise invoice total is 4500."
    )

    vector_store.delete_document(document_id)


def test_delete_document_removes_all_document_vectors(
    vector_store,
):
    document_id = f"test-delete-{uuid4()}"

    point_ids = [
        str(uuid4()),
        str(uuid4()),
        str(uuid4()),
    ]

    vector = [0.2] * vector_store.VECTOR_SIZE

    for point_id in point_ids:
        vector_store.add_vector(
            point_id=point_id,
            vector=vector,
            payload={
                "document_id": document_id,
                "text": "Document chunk.",
            },
        )

    before_delete = vector_store.client.scroll(
        collection_name=vector_store.COLLECTION_NAME,
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id),
                )
            ]
        ),
        limit=100,
        with_payload=True,
    )[0]

    assert len(before_delete) == 3

    vector_store.delete_document(document_id)

    after_delete = vector_store.client.scroll(
        collection_name=vector_store.COLLECTION_NAME,
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id),
                )
            ]
        ),
        limit=100,
        with_payload=True,
    )[0]

    assert after_delete == []


def test_multiple_documents_can_be_stored(
    vector_store,
):
    document_ids = [
        f"test-multi-{uuid4()}",
        f"test-multi-{uuid4()}",
    ]

    vector = [0.3] * vector_store.VECTOR_SIZE

    for document_id in document_ids:
        vector_store.add_vector(
            point_id=str(uuid4()),
            vector=vector,
            payload={
                "document_id": document_id,
                "text": f"Document {document_id}",
            },
        )

    for document_id in document_ids:
        results = vector_store.client.scroll(
            collection_name=vector_store.COLLECTION_NAME,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id),
                    )
                ]
            ),
            limit=100,
            with_payload=True,
        )[0]

        assert len(results) == 1

        vector_store.delete_document(document_id)


def test_vector_size_constant_matches_qdrant_configuration(
    vector_store,
):
    collection_info = vector_store.client.get_collection(
        vector_store.COLLECTION_NAME
    )

    configured_size = collection_info.config.params.vectors.size

    assert configured_size == vector_store.VECTOR_SIZE