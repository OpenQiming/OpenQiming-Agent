import json
from typing import Optional

from agent_platform_basic.extensions.ext_database import async_db
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from agent_platform_basic.libs import DbUtils
from agent_platform_core.models.db_model.model import AppAnnotationSetting, App, AppModelConfig


class AppModelConfigAsync:
    def __init__(self,
                 session: AsyncSession = Depends(DbUtils.get_db_async_session)):
        self.session = session

    async def get_app_model_config(self, app: App):
        if app.app_model_config_id:
            result_model_config = await self.session.execute(
                select(AppModelConfig).filter(AppModelConfig.id == app.app_model_config_id))
            return result_model_config.scalar_one()

        else:
            return None

    def agent_mode_dict(self, app_model_config) -> dict:
        return json.loads(app_model_config.agent_mode) if app_model_config.agent_mode else \
            {"enabled": False, "strategy": None, "tools": [], "prompt": None}

    # async def get_draft_app_model_config(self) -> Optional['AppModelConfig']:
    #     draft_app_model_config = await self.session.execute(
    #         select(AppModelConfig).filter(AppModelConfig.app_id == self.id,
    #                                       AppModelConfig.version == 'draft'))
    #     return draft_app_model_config.scalar_one_or_none()

    async def get_draft_app_model_config(self, app_model) -> Optional['AppModelConfig']:
        draft_app_model_config = await self.session.execute(
            select(AppModelConfig).filter(AppModelConfig.id == app_model.app_model_config_id, AppModelConfig.version == 'draft'))
        return draft_app_model_config.scalar_one_or_none()

    async def get_model_config_fields_async(self, app_model_config):
        if not app_model_config:
            return []

        annotation_setting = await self.session.execute(select(AppAnnotationSetting).filter(
            AppAnnotationSetting.app_id == app_model_config.app_id)
        )
        annotation_setting = annotation_setting.scalar_one_or_none()
        if annotation_setting:
            collection_binding_detail = annotation_setting.collection_binding_detail
            collection_binding_detail_json = {
                "id": annotation_setting.id,
                "enabled": True,
                "score_threshold": annotation_setting.score_threshold,
                "embedding_model": {
                    "embedding_provider_name": collection_binding_detail.provider_name,
                    "embedding_model_name": collection_binding_detail.model_name
                }
            }
        else:
            collection_binding_detail_json = {"enabled": False}

        if app_model_config.dataset_configs:
            dataset_configs = json.loads(app_model_config.dataset_configs)
            if 'retrieval_model' not in dataset_configs:
                dataset_configs_json = {'retrieval_model': 'single'}
            else:
                dataset_configs_json = dataset_configs
        else:
            dataset_configs_json = {'retrieval_model': 'single'}

        return {
            'opening_statement': app_model_config.opening_statement,
            'suggested_questions': json.loads(
                app_model_config.suggested_questions) if app_model_config.suggested_questions else [],
            'suggested_questions_after_answer': json.loads(
                app_model_config.suggested_questions_after_answer) if app_model_config.suggested_questions_after_answer else {
                "enabled": False},
            'speech_to_text': json.loads(app_model_config.speech_to_text) if app_model_config.speech_to_text else {
                "enabled": False},
            'text_to_speech': json.loads(app_model_config.text_to_speech) if app_model_config.text_to_speech else {
                "enabled": False},
            'retriever_resource': json.loads(
                app_model_config.retriever_resource) if app_model_config.retriever_resource else {"enabled": True},
            'annotation_reply': collection_binding_detail_json,
            'more_like_this': json.loads(app_model_config.more_like_this) if app_model_config.more_like_this else {
                "enabled": False},
            'sensitive_word_avoidance': json.loads(
                app_model_config.sensitive_word_avoidance) if app_model_config.sensitive_word_avoidance else {
                "enabled": False, "type": "", "configs": []},
            'external_data_tools': json.loads(
                app_model_config.external_data_tools) if app_model_config.external_data_tools else [],
            'model': json.loads(app_model_config.model) if app_model_config.model else None,
            'user_input_form': json.loads(app_model_config.user_input_form) if app_model_config.user_input_form else [],
            'dataset_query_variable': app_model_config.dataset_query_variable,
            'pre_prompt': app_model_config.pre_prompt,
            'agent_mode': json.loads(app_model_config.agent_mode) if app_model_config.agent_mode else {"enabled": False,
                                                                                                       "strategy": None,
                                                                                                       "tools": [],
                                                                                                       "prompt": None},
            'prompt_type': app_model_config.prompt_type,
            'chat_prompt_config': json.loads(
                app_model_config.chat_prompt_config) if app_model_config.chat_prompt_config else {},
            'completion_prompt_config': json.loads(
                app_model_config.completion_prompt_config) if app_model_config.completion_prompt_config else {},
            'dataset_configs': dataset_configs_json,
            'file_upload': json.loads(app_model_config.file_upload) if app_model_config.file_upload else {
                "image": {"enabled": False, "number_limits": 3, "detail": "high",
                          "transfer_methods": ["remote_url", "local_file"]}},
            'created_at': app_model_config.created_at
        }

    async def async_model_dict(self, app) -> dict:
        return json.loads(app.model) if app.model else None

    async def async_suggested_questions_list(self, app) -> list:
        return json.loads(app.suggested_questions) if app.suggested_questions else []

    async def async_suggested_questions_after_answer_dict(self, app) -> dict:
        return json.loads(app.suggested_questions_after_answer) if app.suggested_questions_after_answer \
            else {"enabled": False}

    async def async_speech_to_text_dict(self, app) -> dict:
        return json.loads(app.speech_to_text) if app.speech_to_text \
            else {"enabled": False}

    async def async_text_to_speech_dict(self, app) -> dict:
        return json.loads(app.text_to_speech) if app.text_to_speech \
            else {"enabled": False}

    async def async_retriever_resource_dict(self, app) -> dict:
        return json.loads(app.retriever_resource) if app.retriever_resource \
            else {"enabled": True}

    async def async_annotation_reply_dict(self, app) -> dict:
        async with async_db.AsyncSessionLocal() as session:
            annotation_setting = await session.execute(select(AppAnnotationSetting).filter(
                AppAnnotationSetting.app_id == app.app_id
            ))
        annotation_setting = annotation_setting.scalar_one_or_none()

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

    async def async_more_like_this_dict(self, app) -> dict:
        return json.loads(app.more_like_this) if app.more_like_this else {"enabled": False}

    async def async_sensitive_word_avoidance_dict(self, app) -> dict:
        return json.loads(app.sensitive_word_avoidance) if app.sensitive_word_avoidance \
            else {"enabled": False, "type": "", "configs": []}

    async def async_external_data_tools_list(self, app) -> list[dict]:
        return json.loads(app.external_data_tools) if app.external_data_tools \
            else []

    async def async_agent_mode_dict(self, app) -> dict:
        return json.loads(app.agent_mode) if app.agent_mode else {"enabled": False, "strategy": None, "tools": [],
                                                                    "prompt": None}

    async def async_chat_prompt_config_dict(self, app) -> dict:
        return json.loads(app.chat_prompt_config) if app.chat_prompt_config else {}

    async def async_completion_prompt_config_dict(self, app) -> dict:
        return json.loads(app.completion_prompt_config) if app.completion_prompt_config else {}

    async def async_dataset_configs_dict(self, app) -> dict:
        if app.dataset_configs:
            dataset_configs = json.loads(app.dataset_configs)
            if 'retrieval_model' not in dataset_configs:
                return {'retrieval_model': 'single'}
            else:
                return dataset_configs
        return {'retrieval_model': 'single'}

    async def async_file_upload_dict(self, app) -> dict:
        return json.loads(app.file_upload) if app.file_upload else {
            "image": {"enabled": False, "number_limits": 3, "detail": "high",
                      "transfer_methods": ["remote_url", "local_file"]}}

    async def async_user_input_form_list(self, app) -> dict:
        return json.loads(app.user_input_form) if app.user_input_form else []

    async def async_to_dict(self, app) -> dict:
        result = {
            "opening_statement": app.opening_statement,
            "suggested_questions": await self.async_suggested_questions_list(app),
            "suggested_questions_after_answer": await self.async_suggested_questions_after_answer_dict(app),
            "speech_to_text": await self.async_speech_to_text_dict(app),
            "text_to_speech": await self.async_text_to_speech_dict(app),
            "retriever_resource": await self.async_retriever_resource_dict(app),
            "annotation_reply": await self.async_annotation_reply_dict(app),
            "more_like_this": await self.async_more_like_this_dict(app),
            "sensitive_word_avoidance": await self.async_sensitive_word_avoidance_dict(app),
            "external_data_tools": await self.async_external_data_tools_list(app),
            "model": await self.async_model_dict(app),
            "user_input_form": await self.async_user_input_form_list(app),
            "dataset_query_variable": app.dataset_query_variable,
            "pre_prompt": app.pre_prompt,
            "agent_mode": await self.async_agent_mode_dict(app),
            "prompt_type": app.prompt_type,
            "chat_prompt_config": await self.async_chat_prompt_config_dict(app),
            "completion_prompt_config": await self.async_completion_prompt_config_dict(app),
            "dataset_configs": await self.async_dataset_configs_dict(app),
            "file_upload": await self.async_file_upload_dict(app)
        }
        return result

