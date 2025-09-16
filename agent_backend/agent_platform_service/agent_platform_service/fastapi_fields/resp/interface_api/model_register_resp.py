"""

@Date    ：2024/9/10 14:39 
@Version: 1.0
@Description:

"""
from typing import Optional

from pydantic import BaseModel


class ModelRegisterResp(BaseModel):
    code: int

    msg: str

    data: Optional[str]
