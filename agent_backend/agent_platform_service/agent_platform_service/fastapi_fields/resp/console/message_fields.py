from typing import Optional

from pydantic import BaseModel

from agent_platform_service.fastapi_fields.resp.console.agent_thought_fields import AgentThoughtFields
from agent_platform_service.fastapi_fields.resp.console.annotation_fields import AnnotationFields
from agent_platform_service.fastapi_fields.resp.console.annotation_hit_history_fields import AnnotationHitHistoryFields
from agent_platform_service.fastapi_fields.resp.console.feedback_fields import FeedbackFields
from agent_platform_service.fastapi_fields.resp.console.message_file_fields import MessageFileFields


class MessageFields(BaseModel):
    id: Optional[str] = None
    conversation_id: Optional[str] = None
    inputs: Optional[dict] = None
    query: Optional[str] = None
    message: Optional[list | str] = None
    message_tokens: Optional[int] = None
    answer: Optional[str] = None
    answer_tokens: Optional[int] = None
    provider_response_latency: Optional[float] = None
    from_source: Optional[str] = None
    from_end_user_id: Optional[str] = None
    from_account_id: Optional[str] = None
    feedbacks: Optional[list[FeedbackFields]] = None
    workflow_run_id: Optional[str] = None
    annotation: Optional[AnnotationFields] = None
    annotation_hit_history: Optional[AnnotationHitHistoryFields] = None
    created_at: Optional[int] = None
    agent_thoughts: Optional[list[AgentThoughtFields]] = None
    message_files: Optional[list[MessageFileFields]] = None
    metadata: Optional[dict] = None
    status: Optional[str] = None
    error: Optional[str] = None
