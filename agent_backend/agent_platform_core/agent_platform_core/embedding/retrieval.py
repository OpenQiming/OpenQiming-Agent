from typing import Optional

from agent_platform_core.models.db_model.dataset import DocumentSegment
from pydantic import BaseModel


class RetrievalChildChunk(BaseModel):
    """Retrieval segments."""

    id: str
    content: str
    score: float
    position: int


class RetrievalSegments(BaseModel):
    """Retrieval segments."""

    model_config = {"arbitrary_types_allowed": True}
    segment: DocumentSegment
    child_chunks: Optional[list[RetrievalChildChunk]] = None
    score: Optional[float] = None
