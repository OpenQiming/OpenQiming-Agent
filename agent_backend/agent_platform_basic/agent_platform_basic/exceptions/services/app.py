from agent_platform_basic.exceptions.services.base import BaseServiceError


class MoreLikeThisDisabledError(BaseServiceError):
    pass


class WorkflowHashNotEqualError(BaseServiceError):
    pass


class AppDeleteError(BaseServiceError):
    pass
