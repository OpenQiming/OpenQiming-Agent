from typing import Optional

from pydantic import BaseModel


class AgentThoughtFields(BaseModel):
    id: Optional[str] = None
    chain_id: Optional[str] = None
    message_id: Optional[str] = None
    position: Optional[int] = None
    thought: Optional[str] = None
    tool: Optional[str] = None
    tool_labels: Optional[str] = None
    tool_input: Optional[str] = None
    created_at: Optional[int] = None
    observation: Optional[str] = None
    files: Optional[list[str]] = None
