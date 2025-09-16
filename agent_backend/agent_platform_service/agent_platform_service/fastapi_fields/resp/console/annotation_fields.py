from pydantic import BaseModel

from agent_platform_service.fastapi_fields.resp.console.account_fields import AccountFields


class AnnotationFields(BaseModel):
    id: str
    question: str
    content: str
    account: AccountFields
    created_at: int