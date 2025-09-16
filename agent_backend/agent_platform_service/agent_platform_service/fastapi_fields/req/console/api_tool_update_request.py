from typing import Optional

from pydantic import BaseModel

class ApiToolUpdateRequest(BaseModel):
    access_type: Optional[int] = 1
    provider: str
    original_provider: Optional[str] = None
    credentials: dict
    icon: dict
    schema_type: str
    schema: str
    labels: Optional[list] = None
    privacy_policy: Optional[str] = None
    custom_disclaimer: Optional[str] = None
    tenant_id: Optional[str] = None
