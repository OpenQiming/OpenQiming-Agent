"""
@Date    ：2024/10/11 10:10 
@Version: 1.0
@Description:

"""
import json

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_platform_basic.libs import DbUtils
from agent_platform_core.models.db_model.model import AppAnnotationSetting


class AppAsync:
    def __init__(self,
                 session: AsyncSession = Depends(DbUtils.get_db_async_session)):
        self.session = session

    def model_dict(self, app_model_config) -> dict:
        return json.loads(app_model_config.model) if app_model_config.model else None

    def suggested_questions_list(self, app_model_config) -> list:
        return json.loads(app_model_config.suggested_questions) if app_model_config.suggested_questions else []

    def suggested_questions_after_answer_dict(self, app_model_config) -> dict:
        return json.loads(
            app_model_config.suggested_questions_after_answer) if app_model_config.suggested_questions_after_answer \
            else {"enabled": False}

    def speech_to_text_dict(self, app_model_config) -> dict:
        return json.loads(app_model_config.speech_to_text) if app_model_config.speech_to_text \
            else {"enabled": False}

    def text_to_speech_dict(self, app_model_config) -> dict:
        return json.loads(app_model_config.text_to_speech) if app_model_config.text_to_speech \
            else {"enabled": False}

    def retriever_resource_dict(self, app_model_config) -> dict:
        return json.loads(app_model_config.retriever_resource) if app_model_config.retriever_resource \
            else {"enabled": True}

    async def annotation_reply_dict(self) -> dict:
        annotation_setting_scalar = await self.session.execute(select(AppAnnotationSetting).filter(
            AppAnnotationSetting.app_id == self.app_id))
        annotation_setting = annotation_setting_scalar.scalar_one_or_none()
        if annotation_setting:
            collection_binding_detail = annotation_setting.collection_binding_detail
            return {
                "id": annotation_setting.id,
                "enabled": True,
                "score_threshold": annotation_setting.score_threshold,
                "embedding_model": {
                    "embedding_provider_name": collection_binding_detail.provider_name,
                    "embedding_model_name": collection_binding_detail.model_name
                }
            }

        else:
            return {"enabled": False}

    def more_like_this_dict(self, app_model_config) -> dict:
        return json.loads(app_model_config.more_like_this) if app_model_config.more_like_this else {"enabled": False}

    def sensitive_word_avoidance_dict(self, app_model_config) -> dict:
        return json.loads(app_model_config.sensitive_word_avoidance) if app_model_config.sensitive_word_avoidance \
            else {"enabled": False, "type": "", "configs": []}

    def external_data_tools_list(self, app_model_config) -> list[dict]:
        return json.loads(app_model_config.external_data_tools) if app_model_config.external_data_tools \
            else []

    def user_input_form_list(self, app_model_config) -> dict:
        return json.loads(app_model_config.user_input_form) if app_model_config.user_input_form else []

    def agent_mode_dict(self, app_model_config) -> dict:
        return json.loads(app_model_config.agent_mode) if app_model_config.agent_mode else {"enabled": False,
                                                                                            "strategy": None,
                                                                                            "tools": [],
                                                                                            "prompt": None}

    def chat_prompt_config_dict(self, app_model_config) -> dict:
        return json.loads(app_model_config.chat_prompt_config) if app_model_config.chat_prompt_config else {}

    def completion_prompt_config_dict(self, app_model_config) -> dict:
        return json.loads(
            app_model_config.completion_prompt_config) if app_model_config.completion_prompt_config else {}

    def dataset_configs_dict(self, app_model_config) -> dict:
        if app_model_config.dataset_configs:
            dataset_configs = json.loads(app_model_config.dataset_configs)
            if 'retrieval_model' not in dataset_configs:
                return {'retrieval_model': 'single'}
            else:
                return dataset_configs
        return {'retrieval_model': 'single'}

    def file_upload_dict(self, app_model_config) -> dict:
        return json.loads(app_model_config.file_upload) if app_model_config.file_upload else {
            "image": {"enabled": False, "number_limits": 3, "detail": "high",
                      "transfer_methods": ["remote_url", "local_file"]}}

    async def to_dict(self, app_model_config) -> dict:
        return {
            "opening_statement": app_model_config.opening_statement,
            "suggested_questions": self.suggested_questions_list(app_model_config),
            "suggested_questions_after_answer": self.suggested_questions_after_answer_dict(app_model_config),
            "speech_to_text": self.speech_to_text_dict(app_model_config),
            "text_to_speech": self.text_to_speech_dict(app_model_config),
            "retriever_resource": self.retriever_resource_dict(app_model_config),
            "annotation_reply": self.annotation_reply_dict,
            "more_like_this": self.more_like_this_dict(app_model_config),
            "sensitive_word_avoidance": self.sensitive_word_avoidance_dict(app_model_config),
            "external_data_tools": self.external_data_tools_list(app_model_config),
            "model": self.model_dict(app_model_config),
            "user_input_form": self.user_input_form_list(app_model_config),
            "dataset_query_variable": app_model_config.dataset_query_variable,
            "pre_prompt": app_model_config.pre_prompt,
            "agent_mode": self.agent_mode_dict(app_model_config),
            "prompt_type": app_model_config.prompt_type,
            "chat_prompt_config": self.chat_prompt_config_dict(app_model_config),
            "completion_prompt_config": self.completion_prompt_config_dict(app_model_config),
            "dataset_configs": self.dataset_configs_dict(app_model_config),
            "file_upload": self.file_upload_dict(app_model_config)
        }
