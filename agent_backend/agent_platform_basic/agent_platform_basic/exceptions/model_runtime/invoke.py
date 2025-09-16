from typing import Optional

"""

@Date    ：2024/7/9 9:00 
@Version: 1.0
@Description:
    
"""


class InvokeError(Exception):
    """Base class for all LLM exceptions."""
    description: Optional[str] = None

    def __init__(self, description: Optional[str] = None) -> None:
        self.description = description

    def __str__(self):
        return self.description or self.__class__.__name__


class InvokeConnectionError(InvokeError):
    """Raised when the Invoke returns connection error."""
    # 调用连接错误
    description = "Connection Error"


class InvokeServerUnavailableError(InvokeError):
    """Raised when the Invoke returns server unavailable error."""
    # 调用服务方不可用
    description = "Server Unavailable Error"


class InvokeRateLimitError(InvokeError):
    """Raised when the Invoke returns rate limit error."""
    # 调用达到限额
    description = "Rate Limit Error"


class InvokeAuthorizationError(InvokeError):
    """Raised when the Invoke returns authorization error."""
    # 调用鉴权失败
    description = "Incorrect model credentials provided, please check and try again. "


class InvokeBadRequestError(InvokeError):
    """Raised when the Invoke returns bad request."""
    # 调用传参有误
    description = "Bad Request Error"
