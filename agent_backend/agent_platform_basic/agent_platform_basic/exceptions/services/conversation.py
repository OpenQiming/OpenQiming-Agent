from agent_platform_basic.exceptions.services.base import BaseServiceError


class LastConversationNotExistsError(BaseServiceError):
    pass


class ConversationNotExistsError(BaseServiceError):
    pass


class ConversationCompletedError(Exception):
    pass
