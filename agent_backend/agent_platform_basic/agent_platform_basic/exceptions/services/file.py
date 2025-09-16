from agent_platform_basic.exceptions.services.base import BaseServiceError


class FileNotExistsError(BaseServiceError):
    pass


class FileTooLargeError(BaseServiceError):
    description = "{message}"


class UnsupportedFileTypeError(BaseServiceError):
    pass
