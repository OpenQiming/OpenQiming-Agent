from agent_platform_basic.exceptions.services.base import BaseServiceError


class DatasetNameDuplicateError(BaseServiceError):
    pass


class DatasetInUseError(BaseServiceError):
    pass
