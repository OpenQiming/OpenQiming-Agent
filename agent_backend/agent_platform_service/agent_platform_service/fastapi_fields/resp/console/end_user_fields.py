from pydantic import BaseModel


class SimpleEndUserFields(BaseModel):
    id: str
    type: str
    is_anonymous: str
    session_id: str
