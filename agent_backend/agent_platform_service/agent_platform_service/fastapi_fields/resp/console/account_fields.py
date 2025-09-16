from pydantic import BaseModel


class AccountFields(BaseModel):
    id: str
    name: str
    email: str