from typing import Optional

from pydantic import BaseModel


class MenuClickResponse(BaseModel):
    message: str

    success: bool
