from typing import Optional

from pydantic import BaseModel


class APIToolDeleteReq(BaseModel):
    provider: str
    tenant_id: Optional[str] = None
