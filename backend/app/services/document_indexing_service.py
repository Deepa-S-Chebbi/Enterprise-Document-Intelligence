from uuid import uuid4

from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.vector_store_service import VectorStoreService


class DocumentIndexingService:
    """
    Converts document text into searchable vector chunks.
    """

    def __init__(
        self,
        chunking_service: ChunkingService | None = None,
        embedding_service: EmbeddingService | None = None,
        vector_store_service: VectorStoreService | None = None,
    ):
        self.chunking_service = (
            chunking_service or ChunkingService()
        )

        self.embedding_service = (
            embedding_service or EmbeddingService()
        )

        self.vector_store_service = (
            vector_store_service or VectorStoreService()
        )

        self.vector_store_service.ensure_collection()

    def index_document(
        self,
        document_id: str,
        text: str,
    ) -> int:
        """
        Chunk a document, generate embeddings, and store
        the resulting vectors in Qdrant.

        Returns the number of indexed chunks.
        """

        chunks = self.chunking_service.split_text(text)

        if not chunks:
            return 0

        embeddings = self.embedding_service.embed_texts(
            chunks
        )

        for index, (chunk, embedding) in enumerate(
            zip(chunks, embeddings)
        ):
            point_id = str(uuid4())

            payload = {
                "document_id": str(document_id),
                "chunk_index": index,
                "text": chunk,
            }

            self.vector_store_service.add_vector(
                point_id=point_id,
                vector=embedding,
                payload=payload,
            )

        return len(chunks)