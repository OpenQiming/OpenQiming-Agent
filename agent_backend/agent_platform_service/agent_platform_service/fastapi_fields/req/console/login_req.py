import re

from pydantic import BaseModel, field_validator

from agent_platform_basic.libs.helper import email as validate_email
from agent_platform_basic.libs.password import check_password_pattern
from typing import List, Dict


class LoginReq(BaseModel):

    email: str

    password: str

    remember_me: bool = False

    @field_validator("email")
    def validate_email(cls, value):
        return validate_email(value)

    @field_validator("password")
    def validate_password(cls, value):
        return check_password_pattern(value)

# 添加产生账号和租户的请求体
class LoginCreateAccountAndTenantReq(BaseModel):
    user_info: Dict[str, str]  # 使用字典
    password: str
    languages: str

    @field_validator('user_info')
    def validate_user_info(cls, value):
        required_keys = {'employeeNumber', 'email', 'name', 'username', 'mobile', 'first_level_company', 'second_level_company'}
        missing_keys = required_keys - set(value.keys())
        if missing_keys:
            raise ValueError(f"Missing required keys in user_info: {missing_keys}")
        return value

    @field_validator("password")
    def validate_password(cls, value):
        return check_password_pattern(value)

    @field_validator('languages')
    def validate_languages(cls, value):
        # 验证 languages 是否合法
        allowed_languages = {'en', 'zh-CN'}
        if value not in allowed_languages:
            raise ValueError(f"Invalid language: {value}. Allowed languages are {allowed_languages}")
        return value

class LoginForSFReq(BaseModel):
    token: str
    signature: str

    @field_validator('token')
    def validate_token(cls, value):
        if not value:
            raise ValueError("token cannot be empty")
        return value

    @field_validator('signature')
    def validate_signature(cls, value):
        if not value:
            raise ValueError("signature cannot be empty")
        return value
