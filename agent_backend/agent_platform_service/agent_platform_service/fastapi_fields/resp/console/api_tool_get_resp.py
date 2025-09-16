from typing import Optional

from pydantic import BaseModel

from agent_platform_core.tools.entities.tool_bundle import ApiToolBundle


class APIToolGetResp(BaseModel):
    schema_type: Optional[str] = None
    schema: Optional[str] = None
    tools: Optional[list[ApiToolBundle]] = []
    icon: Optional[str] = None
    description: Optional[str] = None
    credentials: Optional[dict] = None
    privacy_policy: Optional[str] = None
    custom_disclaimer: Optional[str] = None
    labels:Optional[list[str]] = []

