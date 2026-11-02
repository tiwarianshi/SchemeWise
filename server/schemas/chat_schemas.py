
from pydantic import BaseModel, Field
from typing import Literal


class AskQuestionRequest(BaseModel):
    """Request body for asking a question about government schemes."""

    question: str = Field(
        min_length=3,
        max_length=2000,
        description="Question about information in uploaded scheme documents."
    )

    scheme_id: str | None = None
    document_id: str | None = None


class SourceReference(BaseModel):
    """A document passage used to support an answer."""

    document_id: str
    document_name: str
    page_number: int
    excerpt: str
    source_url: str | None = None


class AskQuestionResponse(BaseModel):
    answer: str
    sources: list[SourceReference] = Field(default_factory=list)
    insufficient_information: bool = False
    answer_status: Literal[
        "complete",
        "partial",
        "insufficient"
    ] = "insufficient"
