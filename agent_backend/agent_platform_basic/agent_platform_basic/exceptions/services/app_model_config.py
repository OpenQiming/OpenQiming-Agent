from agent_platform_basic.exceptions.services.base import BaseServiceError


class AppModelConfigBrokenError(BaseServiceError):
    pass


class AppModelConfigNotExistError(BaseServiceError):
    pass
