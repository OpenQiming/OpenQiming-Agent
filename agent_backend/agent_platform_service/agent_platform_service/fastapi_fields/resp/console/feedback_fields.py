from typing import Optional

from pydantic import BaseModel

from agent_platform_service.fastapi_fields.resp.console.account_fields import AccountFields


class FeedbackFields(BaseModel):
    rating: Optional[str] = None
    content: Optional[str] = None
    from_source: Optional[str] = None
    from_end_user_id: Optional[str] = None
    from_account: Optional[AccountFields] = None
