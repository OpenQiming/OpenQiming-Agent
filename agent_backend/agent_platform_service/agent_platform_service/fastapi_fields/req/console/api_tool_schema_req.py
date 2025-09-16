from pydantic import BaseModel


class APIToolSchemaReq(BaseModel):
    schema: str