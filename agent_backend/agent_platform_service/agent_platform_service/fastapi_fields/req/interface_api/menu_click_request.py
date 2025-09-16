from pydantic import BaseModel


class MenuClickRequest(BaseModel):
    menuName: str | None = None
    menuUrl: str | None = None
    source: str = 'agentplatform'
    employeeNumber: str
