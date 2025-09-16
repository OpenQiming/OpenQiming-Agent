"""

@Date    ：2024/9/10 14:39 
@Version: 1.0
@Description:

"""
from pydantic import BaseModel


class AddApiReq(BaseModel):
    url: str

    type: str = "post"

    name: str

    app_id: str

    createBy: str


class UpdateKeyReq(BaseModel):
    id: str
    appId: str
