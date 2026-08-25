from app.services.rag_generation_service import (
    RAGGenerationService,
)
from app.services.retrieval_pipeline_service import (
    RetrievalPipelineService,
)


class RAGQAService:
    """
    Orchestrates semantic retrieval and LLM generation
    to answer questions using enterprise documents.
    """

    def __init__(
        self,
        retrieval_service: RetrievalPipelineService | None = None,
        generation_service: RAGGenerationService | None = None,
    ):
        self.retrieval_service = (
            retrieval_service
            or RetrievalPipelineService()
        )

        self.generation_service = (
            generation_service
            or RAGGenerationService()
        )

    def answer(
        self,
        query: str,
        limit: int = 5,
        document_id: str | None = None,
    ) -> str:
        """
        Retrieve relevant document chunks and generate
        an answer using those chunks as context.
        """

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        if limit <= 0:
            raise ValueError(
                "Limit must be greater than 0."
            )

        if document_id is None:
            results = self.retrieval_service.retrieve(
                query=query,
                limit=limit,
            )
        else:
            results = self.retrieval_service.retrieve(
                query=query,
                limit=limit,
                document_id=document_id,
            )

        if not results:
            return (
                "I could not find relevant information "
                "in the provided documents."
            )

        context = []

        for result in results:
            if isinstance(result, str):
                context.append(result)
                continue

            payload = getattr(result, "payload", None)

            if not payload:
                continue

            text = payload.get("text")

            if text and text.strip():
                context.append(text)

        if not context:
            return (
                "I could not find relevant information "
                "in the provided documents."
            )

        return self.generation_service.generate_answer(
            query=query,
            context=context,
        )