from app.services.embedding_service import EmbeddingService
from app.services.semantic_retrieval_service import (
    SemanticRetrievalService,
)
from app.services.vector_store_service import VectorStoreService


class RetrievalPipelineService:
    """
    Orchestrates retrieval of relevant document chunks.
    """

    DEFAULT_LIMIT = 5

    def __init__(
        self,
        semantic_retrieval_service=None,
    ):
        self.semantic_retrieval_service = (
            semantic_retrieval_service
            or SemanticRetrievalService(
                embedding_service=EmbeddingService(),
                vector_store=VectorStoreService(),
            )
        )

    def retrieve(
        self,
        query: str,
        limit: int = DEFAULT_LIMIT,
        document_id: str | None = None,
    ):
        """
        Retrieve the most relevant document chunks
        for a natural-language query.
        """

        if not query or not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        if limit <= 0:
            raise ValueError(
                "Limit must be greater than 0."
            )

        if document_id is None:
            return self.semantic_retrieval_service.retrieve(
                query,
                limit=limit,
            )

        return self.semantic_retrieval_service.retrieve(
            query,
            limit=limit,
            document_id=document_id,
        )