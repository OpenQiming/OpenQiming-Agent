from pydantic import BaseModel


class ApiToolResponse(BaseModel):
    provider_id: str
    result: str