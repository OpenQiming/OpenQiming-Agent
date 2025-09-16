from typing import Optional

from pydantic import BaseModel

from agent_platform_service.fastapi_fields.resp.console.account_fields import AccountFields


class AnnotationHitHistoryFields(BaseModel):
    annotation_id: Optional[str] = None
    annotation_create_account: Optional[AccountFields] = None
    created_at: Optional[int] = None
