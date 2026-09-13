from typing import Any, Literal
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)

    user_role: Literal[
        "sales",
        "support",
        "management",
        "admin",
    ] = "support"

class Citation(BaseModel):
    citation_id: str
    document_id: str
    document_name: str
    version: str
    section_title: str
    source_path: str

class ChatResponse(BaseModel):
    request_id: str
    answer: str
    citations: list[Citation] = Field(
        default_factory=list
    )
    trace: list[dict[str, Any]]
