from agent_platform_basic.exceptions.base_http_exception import BaseHTTPException


class ApplicationAlreadyCreatedError(BaseHTTPException):
    # error_code = '流程已经创建，并且状态为 PENDING'
    error_code = '流程已创建，等待项目管理员审批'

    # description = "流程已经创建，并且状态为 PENDING"
    description = "流程已创建，等待项目管理员审批"
    result = 'error'
    code = 200
