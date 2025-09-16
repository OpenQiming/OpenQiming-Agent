from pydantic import BaseModel


class FeedBackStatFields(BaseModel):
    like: int
    dislike: int
