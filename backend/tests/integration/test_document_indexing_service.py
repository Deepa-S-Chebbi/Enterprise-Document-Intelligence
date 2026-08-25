from uuid import uuid4

from app.services.document_indexing_service import DocumentIndexingService
from app.services.embedding_service import EmbeddingService
from app.services.vector_store_service import VectorStoreService


def test_document_indexing_creates_searchable_vectors():
    document_id = f"test-index-{uuid4()}"

    text = (
        "Enterprise invoice for customer ABC. "
        "Invoice number INV-TEST-001. "
        "The total invoice amount is 4500. "
        "Payment is due within 30 days."
    )

    indexing_service = DocumentIndexingService()

    indexed_count = indexing_service.index_document(
        document_id=document_id,
        text=text,
    )

    assert indexed_count >= 1

    # ------------------------------------------------------------
    # Verify the indexed document through the vector store
    # ------------------------------------------------------------

    embedding_service = EmbeddingService()
    vector_store = VectorStoreService()

    query_vector = embedding_service.embed_text(
        "What is the invoice total amount?"
    )

    # Use a larger result set during verification so the test
    # does not depend on the document being in the top 3 results.
    results = vector_store.search(
        query_vector,
        limit=10,
    )

    print("\n===== SEARCH RESULTS =====")
    print("Expected document_id:", document_id)
    print("Result count:", len(results))

    for result in results:
        payload = result.payload or {}

        print(
            "score=",
            result.score,
            "| document_id=",
            payload.get("document_id"),
            "| text=",
            payload.get("text"),
        )

    matching_results = [
        result
        for result in results
        if result.payload
        and result.payload.get("document_id") == document_id
    ]

    print("Matching results:", len(matching_results))

    assert matching_results, (
        f"Indexed document {document_id} was not found "
        f"in the vector search results."
    )

    payload = matching_results[0].payload

    assert payload["document_id"] == document_id
    assert "INV-TEST-001" in payload["text"]
    assert "4500" in payload["text"]

    # ------------------------------------------------------------
    # Cleanup test vectors
    # ------------------------------------------------------------

    vector_store.delete_document(document_id)