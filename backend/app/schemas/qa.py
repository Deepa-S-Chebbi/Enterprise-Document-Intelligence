from pydantic import BaseModel, Field


class QARequest(BaseModel):
    query: str = Field(..., min_length=1, description="The question to ask.")
    document_id: str | None = Field(
        default=None,
        description="Restrict retrieval to a single document. "
        "Omit to search across all indexed documents.",
    )
    limit: int = Field(
        default=5,
        gt=0,
        description="Number of context chunks to retrieve.",
    )


class QAResponse(BaseModel):
    query: str
    document_id: str | None
    answer: str
