import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_rag_qa_service
from app.exceptions.extraction_exceptions import LLMProviderError
from app.schemas.qa import QARequest, QAResponse
from app.services.rag_qa_service import RAGQAService

router = APIRouter()

logger = logging.getLogger(__name__)


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
        raise HTTPException(
            status_code=400,
            detail=str(e),
        ) from e

    except LLMProviderError as e:
        # Log the raw provider error internally,
        # but never expose it to the client.
        logger.error(
            "LLM provider error during RAG QA: %s",
            e,
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "The AI service is temporarily unavailable. "
                "Please try again later."
            ),
        ) from e

    except Exception as e:
        # Log unexpected downstream errors internally,
        # but return a safe message to the client.
        logger.error(
            "Unexpected RAG pipeline error: %s",
            e,
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "The document question-answering service is "
                "temporarily unavailable. Please try again later."
            ),
        ) from e

    return QAResponse(
        query=payload.query,
        document_id=payload.document_id,
        answer=answer,
    )