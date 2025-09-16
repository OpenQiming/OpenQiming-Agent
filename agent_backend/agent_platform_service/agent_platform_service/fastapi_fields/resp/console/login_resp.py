from pydantic import BaseModel


class LoginResp(BaseModel):

    result: str

    data: str

class LoginCreateAccountAndTenantResp(BaseModel):
    result: str

    code: str
