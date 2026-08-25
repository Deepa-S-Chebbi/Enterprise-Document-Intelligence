from uuid import UUID

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)


class VectorStoreService:
    """
    Handles vector storage and similarity search using Qdrant.
    """

    COLLECTION_NAME = "document_chunks"
    VECTOR_SIZE = 384

    def __init__(
        self,
        url: str = "http://localhost:6333",
    ):
        self.client = QdrantClient(url=url)

    def ensure_collection(self) -> None:
        """
        Create the document chunk collection if it does not exist.
        """

        collections = self.client.get_collections()

        existing_names = {
            collection.name
            for collection in collections.collections
        }

        if self.COLLECTION_NAME not in existing_names:
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=self.VECTOR_SIZE,
                    distance=Distance.COSINE,
                ),
            )

    def add_vector(
        self,
        point_id: str | UUID,
        vector: list[float],
        payload: dict,
    ) -> None:
        """
        Store a single vector with metadata.
        """

        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=[
                PointStruct(
                    id=str(point_id),
                    vector=vector,
                    payload=payload,
                )
            ],
        )

    def search(
        self,
        vector: list[float],
        limit: int = 5,
        document_id: str | None = None,
    ):
        """
        Search for the most similar document chunks.

        If document_id is provided, retrieval is restricted
        to chunks belonging to that document.
        """

        query_filter = None

        if document_id:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id),
                    )
                ]
            )

        return self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=vector,
            query_filter=query_filter,
            limit=limit,
        ).points

    def delete_document(
        self,
        document_id: str,
    ) -> None:
        """
        Delete all vectors belonging to a document.
        """

        self.client.delete(
            collection_name=self.COLLECTION_NAME,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id),
                    )
                ]
            ),
        )