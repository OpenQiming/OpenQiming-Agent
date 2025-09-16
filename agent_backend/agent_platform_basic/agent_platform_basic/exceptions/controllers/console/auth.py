from agent_platform_basic.exceptions.base_http_exception import BaseHTTPException


class ApiKeyAuthFailedError(BaseHTTPException):
    error_code = 'auth_failed'
    description = "{message}"
    code = 500