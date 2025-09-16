from agent_platform_basic.exceptions.services.base import BaseServiceError


class FirstMessageNotExistsError(BaseServiceError):
    pass


class LastMessageNotExistsError(BaseServiceError):
    pass


class MessageNotExistsError(BaseServiceError):
    pass


class SuggestedQuestionsAfterAnswerDisabledError(BaseServiceError):
    pass
