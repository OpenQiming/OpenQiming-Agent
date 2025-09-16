from typing import Optional

from pydantic import BaseModel, Field

""" 

@Date    ：2024/7/22 23:00 
@Version: 1.0
@Description:
    Swagger Check Auth Configuration
"""


class SwaggerConfig(BaseModel):
    """
    Swagger configs
    """
    SWAGGER_USERNAME: Optional[str] = Field(
        description='Swagger username',
        default=None,
    )

    SWAGGER_PASSWORD: Optional[str] = Field(
        description='Swagger password',
        default=None,
    )
