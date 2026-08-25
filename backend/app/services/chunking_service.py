class ChunkingService:
    """
    Splits document text into overlapping chunks suitable
    for embedding and vector search.
    """

    DEFAULT_CHUNK_SIZE = 1000
    DEFAULT_OVERLAP = 200

    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        overlap: int = DEFAULT_OVERLAP,
    ):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")

        if overlap < 0:
            raise ValueError("overlap cannot be negative")

        if overlap >= chunk_size:
            raise ValueError(
                "overlap must be smaller than chunk_size"
            )

        self.chunk_size = chunk_size
        self.overlap = overlap

    def split_text(self, text: str) -> list[str]:
        """
        Split text into overlapping chunks.

        Example:
            chunk_size=1000
            overlap=200

        Chunk 1: characters 0-999
        Chunk 2: characters 800-1799
        Chunk 3: characters 1600-2599
        """

        if not text or not text.strip():
            return []

        text = text.strip()

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end >= len(text):
                break

            start = end - self.overlap

        return chunks