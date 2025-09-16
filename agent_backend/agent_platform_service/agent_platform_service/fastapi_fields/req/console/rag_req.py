from pydantic import BaseModel, field_validator

class UploadFileForRagReq(BaseModel):

    file: str

    remember_me: bool = False

    # @field_validator("email")
    # def validate_email(cls, value):
    #     return validate_email(value)

    # @field_validator("password")
    # def validate_password(cls, value):
    #     return check_password_pattern(value)