from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_rag_qa_service
from app.exceptions.extraction_exceptions import LLMProviderError
from app.schemas.qa import QARequest, QAResponse
from app.services.rag_qa_service import RAGQAService

router = APIRouter()


@router.post(
    "/qa",
    response_model=QAResponse,
    summary="Ask a question about the indexed document(s)",
)
def ask_question(
    payload: QARequest,
    service: RAGQAService = Depends(get_rag_qa_service),
) -> QAResponse:
    try:
        answer = service.answer(
            query=payload.query,
            limit=payload.limit,
            document_id=payload.document_id,
        )
    except ValueError as e:
        # Bad input (empty query, invalid limit, etc.)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except LLMProviderError as e:
        # Upstream LLM provider (Gemini) failed
        raise HTTPException(status_code=502, detail=str(e)) from e
    except Exception as e:
        # Any other downstream dependency failure (e.g. vector store
        # unreachable) is treated as a bad gateway rather than a 500,
        # since the API layer itself did nothing wrong.
        raise HTTPException(
            status_code=502,
            detail=f"RAG pipeline is currently unavailable: {e}",
        ) from e

    return QAResponse(
        query=payload.query,
        document_id=payload.document_id,
        answer=answer,
    )
