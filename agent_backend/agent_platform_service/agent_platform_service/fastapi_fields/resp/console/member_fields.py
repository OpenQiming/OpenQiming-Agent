from pydantic import BaseModel
from typing import Optional

from agent_platform_basic.models.db_model import Account


class SimpleAccountFields(BaseModel):
    id: str
    name: str
    email: str
    employee_number: Optional[str] = None
    mobile: Optional[str] = None
    company_name: Optional[str] = None
    first_level_company: Optional[str] = None
    second_level_company: Optional[str] = None

    def __init__(self, account: 'Account') -> None:
        data = {
            'id': account.id,
            'name': account.name,
            'email': account.email,
            'employee_number': account.employee_number,
            'mobile': account.mobile,
            'company_name': account.company_name,
            'first_level_company': account.first_level_company,
            'second_level_company': account.second_level_company,
        }
        super().__init__(**data)

    @classmethod
    async def from_account(cls, account: Account) :
        return cls(account)



class ListAccountFields(SimpleAccountFields):
    workflow_count: int = 0
    agent_chat_count: int = 0
    chat_count: int = 0
    tenant_info: list[dict[str, str]] = []

class DetailAccountFields(SimpleAccountFields):
    tenant_info: list[dict[str, str]] = []
    workflow_info: list[dict[str, str]] = []
    agent_info: list[dict[str, str]] = []


