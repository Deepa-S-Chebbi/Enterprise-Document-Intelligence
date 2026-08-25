from uuid import uuid4

from app.services.document_indexing_service import (
    DocumentIndexingService,
)
from app.services.rag_qa_service import RAGQAService
from app.services.vector_store_service import (
    VectorStoreService,
)


def test_end_to_end_rag_document_qa():
    document_id = f"test-rag-{uuid4()}"

    document_text = (
        "Enterprise invoice for customer Acme Corporation. "
        "Invoice number is INV-RAG-001. "
        "The total invoice amount is 8750 USD. "
        "Payment is due within 30 days. "
        "The invoice was issued on August 20, 2026."
    )

    indexing_service = DocumentIndexingService()
    vector_store = VectorStoreService()
    rag_service = RAGQAService()

    indexed_count = indexing_service.index_document(
        document_id=document_id,
        text=document_text,
    )

    assert indexed_count >= 1

    try:
        answer = rag_service.answer(
    query="What is the total invoice amount?",
    limit=5,
    document_id=document_id,
)

        print("\n================ RAG ANSWER ================")
        print(answer)
        print("=============================================\n")

        assert answer
        assert isinstance(answer, str)
        assert len(answer.strip()) > 0

        assert "8750" in answer

    finally:
        vector_store.delete_document(
            document_id
        )