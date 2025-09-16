from typing import Optional

from pydantic import BaseModel


class ApiToolTestResponse(BaseModel):
    result: Optional[str] = None
    error: Optional[str] = None