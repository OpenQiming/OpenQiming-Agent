from typing import Optional
from typing import Dict, Any
from pydantic import BaseModel


class APIToolTestPreRequest(BaseModel):
    tool_name: str
    provider_name: Optional[str] = None
    credentials: dict
    parameters: dict
    schema_type: str
    schema: str
    tenant_id: Optional[str] = None

class APIToolTest(BaseModel):
    url: str
    methods: str
    headers: Dict[str, str]
    body: Dict[str, Any]