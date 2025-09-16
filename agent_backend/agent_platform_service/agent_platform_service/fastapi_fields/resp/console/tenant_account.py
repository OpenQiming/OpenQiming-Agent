from typing import Optional, List

from pydantic import BaseModel



class TenantAccountResp(BaseModel):
    account_id: Optional[str] = None
    role: Optional[str] = None
    name: Optional[str] = None
    employee_number: Optional[str] = None
