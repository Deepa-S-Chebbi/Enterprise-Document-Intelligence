from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """
    Generates vector embeddings for text using
    a local Sentence Transformers model.
    """

    MODEL_NAME = "all-MiniLM-L6-v2"

    def __init__(self):
        self.model = SentenceTransformer(
            self.MODEL_NAME
        )

    def embed_text(self, text: str) -> list[float]:
        """
        Generate an embedding vector for a single text.
        """

        if not text or not text.strip():
            raise ValueError(
                "Text cannot be empty."
            )

        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        return embedding.tolist()

    def embed_texts(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.
        """

        if not texts:
            raise ValueError(
                "Texts cannot be empty."
            )

        if any(
            not text or not text.strip()
            for text in texts
        ):
            raise ValueError(
                "Texts cannot contain empty values."
            )

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
        )

        return embeddings.tolist()