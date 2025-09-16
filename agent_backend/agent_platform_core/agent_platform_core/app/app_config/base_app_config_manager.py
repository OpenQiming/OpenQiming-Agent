from collections.abc import Mapping
from typing import Any

from agent_platform_core.app.app_config.entities import AppAdditionalFeatures
from agent_platform_core.app.app_config.features.file_upload.manager import FileUploadConfigManager
from agent_platform_core.app.app_config.features.more_like_this.manager import MoreLikeThisConfigManager
from agent_platform_core.app.app_config.features.opening_statement.manager import OpeningStatementConfigManager
from agent_platform_core.app.app_config.features.retrieval_resource.manager import RetrievalResourceConfigManager
from agent_platform_core.app.app_config.features.speech_to_text.manager import SpeechToTextConfigManager
from agent_platform_core.app.app_config.features.suggested_questions_after_answer.manager import (
    SuggestedQuestionsAfterAnswerConfigManager,
)
from agent_platform_core.app.app_config.features.text_to_speech.manager import TextToSpeechConfigManager
from agent_platform_core.models.enum_model.app_mode import AppMode


class BaseAppConfigManager:
    @classmethod
    def convert_features(cls, config_dict: Mapping[str, Any], app_mode: AppMode) -> AppAdditionalFeatures:
        """
        Convert app config to app model config

        :param config_dict: app config
        :param app_mode: app mode
        """
        config_dict = dict(config_dict.items())

        additional_features = AppAdditionalFeatures()
        additional_features.show_retrieve_source = RetrievalResourceConfigManager.convert(config=config_dict)

        additional_features.file_upload = FileUploadConfigManager.convert(
            config=config_dict, is_vision=app_mode in {AppMode.CHAT, AppMode.COMPLETION, AppMode.AGENT_CHAT}
        )

        additional_features.opening_statement, additional_features.suggested_questions = (
            OpeningStatementConfigManager.convert(config=config_dict)
        )

        additional_features.suggested_questions_after_answer = SuggestedQuestionsAfterAnswerConfigManager.convert(
            config=config_dict
        )

        additional_features.more_like_this = MoreLikeThisConfigManager.convert(config=config_dict)

        additional_features.speech_to_text = SpeechToTextConfigManager.convert(config=config_dict)

        additional_features.text_to_speech = TextToSpeechConfigManager.convert(config=config_dict)

        return additional_features
