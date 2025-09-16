from pydantic import BaseModel


class WebsocketMetabolicResp(BaseModel):
    type: str

    data: str | dict
