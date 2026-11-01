
import logging

from fastapi import APIRouter, HTTPException

from schemas.chat_schemas import (
    AskQuestionRequest,
    AskQuestionResponse,
)
from services.rag_service import RAGService


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)

# Create the service only when the first question arrives.
_rag_service = None


def get_rag_service():
    global _rag_service

    if _rag_service is None:
        _rag_service = RAGService()

    return _rag_service


@router.post("/ask", response_model=AskQuestionResponse)
def ask_question(request: AskQuestionRequest):
    """Answer a question using uploaded government scheme documents."""

    try:
        service = get_rag_service()

        result = service.ask(
            question=request.question,
            scheme_id=request.scheme_id,
            document_id=request.document_id,
        )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        logger.exception("RAG question-answering failed")

        raise HTTPException(
            status_code=500,
            detail="Unable to process the question right now.",
        ) from error
