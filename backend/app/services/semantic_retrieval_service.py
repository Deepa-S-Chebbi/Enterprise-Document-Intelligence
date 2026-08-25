class SemanticRetrievalService:
    """
    Retrieves semantically similar document chunks
    using query embeddings and vector similarity search.
    """

    DEFAULT_LIMIT = 5

    def __init__(
        self,
        embedding_service,
        vector_store,
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        limit: int = DEFAULT_LIMIT,
        document_id: str | None = None,
    ):
        """
        Generate an embedding for the query and retrieve
        the most semantically similar document chunks.

        If document_id is provided, retrieval is restricted
        to chunks belonging to that document.
        """

        if not query or not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        if limit <= 0:
            raise ValueError(
                "Limit must be greater than 0."
            )

        query_embedding = (
            self.embedding_service.embed_text(
                query
            )
        )

        if document_id is None:
            return self.vector_store.search(
                vector=query_embedding,
                limit=limit,
            )

        return self.vector_store.search(
            vector=query_embedding,
            limit=limit,
            document_id=document_id,
        )