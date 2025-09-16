from typing import Optional

from pydantic import BaseModel


class MessageFileFields(BaseModel):
    id: Optional[str] = None
    type: Optional[str] = None
    url: Optional[str] = None
    belongs_to: Optional[str] = None
