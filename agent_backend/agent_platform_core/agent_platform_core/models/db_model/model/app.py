import json
import uuid
from typing import Optional

from flask import current_app, request
from sqlalchemy import text, JSON, select
from sqlalchemy.orm import Mapped

from agent_platform_basic.extensions.ext_database import db, Base, async_db
from agent_platform_basic.models.db_model import StringUUID, Tenant
from agent_platform_core.models.enum_model.app_mode import AppMode
from agent_platform_core.models.db_model.workflow import Workflow
from .app_annotation_setting import AppAnnotationSetting
from .site import Site
from .tag import Tag
from .tag_binding import TagBinding
from sqlalchemy import Column, String, DateTime, text, PrimaryKeyConstraint, Index, Text, Boolean, Integer

"""
@Date    ：2024/7/14 23:46 
@Version: 1.0
@Description:

"""


class App(Base):
    __tablename__ = 'apps'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='app_pkey'),
        Index('app_tenant_id_idx', 'tenant_id')
    )

    id = Column(StringUUID, server_default=text('uuid_generate_v4()'))
    tenant_id: Mapped[str] = Column(StringUUID, nullable=False)
    account_id = Column(StringUUID, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False, server_default=text("''::character varying"))
    mode = Column(String(255), nullable=False)
    icon = Column(String(255))
    icon_background = Column(String(255))
    app_model_config_id = Column(StringUUID, nullable=True)
    workflow_id = Column(StringUUID, nullable=True)
    status = Column(String(255), nullable=False, server_default=text("'draft'::character varying"))
    enable_site = Column(Boolean, nullable=False)
    enable_api = Column(Boolean, nullable=False)
    api_rpm = Column(Integer, nullable=False, server_default=text('0'))
    api_rph = Column(Integer, nullable=False, server_default=text('0'))
    is_demo = Column(Boolean, nullable=False, server_default=text('false'))
    is_public = Column(Boolean, nullable=False, server_default=text('false'))
    is_universal = Column(Boolean, nullable=False, server_default=text('false'))
    tracing = Column(Text, nullable=True)
    header_image = Column(Text, nullable=True)
    max_active_requests = Column(Integer, nullable=True)
    created_by = Column(StringUUID, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))
    updated_by = db.Column(StringUUID, nullable=True)
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))
    use_icon_as_answer_icon = db.Column(db.Boolean, nullable=False, server_default=db.text("false"))
    experience_count = Column(Integer, nullable=False, server_default="0")
    subscription_count = Column(Integer, nullable=False, server_default="0")
    like_count = Column(Integer, nullable=False, server_default="0")
    app_type = Column(String, nullable=True)

    @property
    def desc_or_prompt(self):
        if self.description:
            return self.description
        else:
            app_model_config = self.app_model_config
            if app_model_config:
                return app_model_config.pre_prompt
            else:
                return ''

    @property
    def site(self):
        site = db.session.query(Site).filter(Site.app_id == self.id).first()
        return site

    @property
    def app_model_config(self) -> Optional['AppModelConfig']:
        if self.app_model_config_id:
            return db.session.query(AppModelConfig).filter(AppModelConfig.id == self.app_model_config_id).first()

        return None

    @property
    def draft_app_model_config(self) -> Optional['AppModelConfig']:
        return db.session.query(AppModelConfig).filter(AppModelConfig.app_id == self.id,
                                                       AppModelConfig.version == 'draft',
                                                       AppModelConfig.id == self.app_model_config_id).first()

    @property
    def workflow(self) -> Optional['Workflow']:
        if self.workflow_id:
            return db.session.query(Workflow).filter(Workflow.id == self.workflow_id).first()

        return None

    @property
    def api_base_url(self):
        return (current_app.config['SERVICE_API_URL'] if current_app.config['SERVICE_API_URL']
                else request.host_url.rstrip('/')) + '/v1'

    @property
    def tenant(self):
        tenant = db.session.query(Tenant).filter(Tenant.id == self.tenant_id).first()
        return tenant

    @property
    def is_agent(self) -> bool:
        app_model_config = self.app_model_config
        if not app_model_config:
            return False
        if not app_model_config.agent_mode:
            return False
        if self.app_model_config.agent_mode_dict.get('enabled', False) \
                and self.app_model_config.agent_mode_dict.get('strategy', '') in ['function_call', 'react']:
            self.mode = AppMode.AGENT_CHAT.value
            db.session.commit()
            return True
        return False

    @property
    def mode_compatible_with_agent(self) -> str:
        if self.mode == AppMode.CHAT.value and self.is_agent:
            return AppMode.AGENT_CHAT.value

        return self.mode

    @property
    def deleted_tools(self) -> list:
        # get agent mode tools
        app_model_config = self.app_model_config
        if not app_model_config:
            return []
        if not app_model_config.agent_mode:
            return []
        agent_mode = app_model_config.agent_mode_dict
        tools = agent_mode.get('tools', [])

        provider_ids = []

        for tool in tools:
            keys = list(tool.keys())
            if len(keys) >= 4:
                provider_type = tool.get('provider_type', '')
                provider_id = tool.get('provider_id', '')
                if provider_type == 'api':
                    # check if provider id is a uuid string, if not, skip
                    try:
                        uuid.UUID(provider_id)
                    except Exception:
                        continue
                    provider_ids.append(provider_id)

        if not provider_ids:
            return []

        api_providers = db.session.execute(
            text('SELECT id FROM tool_api_providers WHERE id IN :provider_ids'),
            {'provider_ids': tuple(provider_ids)}
        ).fetchall()

        deleted_tools = []
        current_api_provider_ids = [str(api_provider.id) for api_provider in api_providers]

        for tool in tools:
            keys = list(tool.keys())
            if len(keys) >= 4:
                provider_type = tool.get('provider_type', '')
                provider_id = tool.get('provider_id', '')
                if provider_type == 'api' and provider_id not in current_api_provider_ids:
                    deleted_tools.append(tool['tool_name'])

        return deleted_tools

    # @property
    # def tags(self):
    #     tags = db.session.query(Tag).join(
    #         TagBinding,
    #         Tag.id == TagBinding.tag_id
    #     ).filter(
    #         TagBinding.target_id == self.id,
    #         TagBinding.tenant_id == self.tenant_id,
    #         Tag.tenant_id == self.tenant_id,
    #         Tag.type == 'app'
    #     ).all()
    #
    #     return tags if tags else []

class PublishApp(Base):
    __tablename__ = 'publish_apps'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='app_pkey'),
    )

    id = Column(StringUUID, server_default=text('uuid_generate_v4()'))
    current_app_id = Column(StringUUID, nullable=False)
    version_app_id = Column(StringUUID, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))

class AppModelConfig(Base):
    __tablename__ = 'app_model_configs'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='app_model_config_pkey'),
        Index('app_app_id_idx', 'app_id')
    )

    id = Column(StringUUID, server_default=text('uuid_generate_v4()'))
    app_id = Column(StringUUID, nullable=False)
    version = Column(String(255), nullable=False)
    provider = Column(String(255), nullable=True)
    model_id = Column(String(255), nullable=True)
    configs = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))
    opening_statement = Column(Text)
    suggested_questions = Column(Text)
    suggested_questions_after_answer = Column(Text)
    speech_to_text = Column(Text)
    text_to_speech = Column(Text)
    more_like_this = Column(Text)
    model = Column(Text)
    user_input_form = Column(Text)
    dataset_query_variable = Column(String(255))
    pre_prompt = Column(Text)
    agent_mode = Column(Text)
    sensitive_word_avoidance = Column(Text)
    retriever_resource = Column(Text)
    prompt_type = Column(String(255), nullable=False, server_default=text("'simple'::character varying"))
    chat_prompt_config = Column(Text)
    completion_prompt_config = Column(Text)
    dataset_configs = Column(Text)
    external_data_tools = Column(Text)
    file_upload = Column(Text)
    is_enable = Column(Boolean, nullable=False, default=True)
    version_app_name = Column(Text)
    version_created_by = Column(StringUUID)

    @property
    def app(self):
        app = db.session.query(App).filter(App.id == self.app_id).first()
        return app

    @property
    def model_dict(self) -> dict:
        return json.loads(self.model) if self.model else None

    @property
    def suggested_questions_list(self) -> list:
        return json.loads(self.suggested_questions) if self.suggested_questions else []

    @property
    def suggested_questions_after_answer_dict(self) -> dict:
        return json.loads(self.suggested_questions_after_answer) if self.suggested_questions_after_answer \
            else {"enabled": False}

    @property
    def speech_to_text_dict(self) -> dict:
        return json.loads(self.speech_to_text) if self.speech_to_text \
            else {"enabled": False}

    @property
    def text_to_speech_dict(self) -> dict:
        return json.loads(self.text_to_speech) if self.text_to_speech \
            else {"enabled": False}

    @property
    def retriever_resource_dict(self) -> dict:
        return json.loads(self.retriever_resource) if self.retriever_resource \
            else {"enabled": True}

    @property
    def annotation_reply_dict(self) -> dict:
        annotation_setting = db.session.query(AppAnnotationSetting).filter(
            AppAnnotationSetting.app_id == self.app_id).first()
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

    @property
    def more_like_this_dict(self) -> dict:
        return json.loads(self.more_like_this) if self.more_like_this else {"enabled": False}

    @property
    def sensitive_word_avoidance_dict(self) -> dict:
        return json.loads(self.sensitive_word_avoidance) if self.sensitive_word_avoidance \
            else {"enabled": False, "type": "", "configs": []}

    @property
    def external_data_tools_list(self) -> list[dict]:
        return json.loads(self.external_data_tools) if self.external_data_tools \
            else []

    @property
    def user_input_form_list(self) -> dict:
        return json.loads(self.user_input_form) if self.user_input_form else []

    @property
    def agent_mode_dict(self) -> dict:
        return json.loads(self.agent_mode) if self.agent_mode else {"enabled": False, "strategy": None, "tools": [],
                                                                    "prompt": None}

    @property
    def chat_prompt_config_dict(self) -> dict:
        return json.loads(self.chat_prompt_config) if self.chat_prompt_config else {}

    @property
    def completion_prompt_config_dict(self) -> dict:
        return json.loads(self.completion_prompt_config) if self.completion_prompt_config else {}

    @property
    def dataset_configs_dict(self) -> dict:
        if self.dataset_configs:
            dataset_configs = json.loads(self.dataset_configs)
            if 'retrieval_model' not in dataset_configs:
                return {'retrieval_model': 'single'}
            else:
                return dataset_configs
        return {'retrieval_model': 'single'}

    @property
    def file_upload_dict(self) -> dict:
        return json.loads(self.file_upload) if self.file_upload else {
            "image": {"enabled": False, "number_limits": 3, "detail": "high",
                      "transfer_methods": ["remote_url", "local_file"]}}

    def to_dict(self) -> dict:
        return {
            "opening_statement": self.opening_statement,
            "suggested_questions": self.suggested_questions_list,
            "suggested_questions_after_answer": self.suggested_questions_after_answer_dict,
            "speech_to_text": self.speech_to_text_dict,
            "text_to_speech": self.text_to_speech_dict,
            "retriever_resource": self.retriever_resource_dict,
            # todo 改异步
            # "annotation_reply": self.annotation_reply_dict,
            "annotation_reply": {"enabled": False},
            "more_like_this": self.more_like_this_dict,
            "sensitive_word_avoidance": self.sensitive_word_avoidance_dict,
            "external_data_tools": self.external_data_tools_list,
            "model": self.model_dict,
            "user_input_form": self.user_input_form_list,
            "dataset_query_variable": self.dataset_query_variable,
            "pre_prompt": self.pre_prompt,
            "agent_mode": self.agent_mode_dict,
            "prompt_type": self.prompt_type,
            "chat_prompt_config": self.chat_prompt_config_dict,
            "completion_prompt_config": self.completion_prompt_config_dict,
            "dataset_configs": self.dataset_configs_dict,
            "file_upload": self.file_upload_dict
        }

    def from_model_config_dict(self, model_config: dict):
        self.opening_statement = model_config.get('opening_statement')
        self.suggested_questions = json.dumps(model_config['suggested_questions'], ensure_ascii=False) \
            if model_config.get('suggested_questions') else None
        self.suggested_questions_after_answer = json.dumps(model_config['suggested_questions_after_answer'],
                                                           ensure_ascii=False) \
            if model_config.get('suggested_questions_after_answer') else None
        self.speech_to_text = json.dumps(model_config['speech_to_text'], ensure_ascii=False) \
            if model_config.get('speech_to_text') else None
        self.text_to_speech = json.dumps(model_config['text_to_speech'], ensure_ascii=False) \
            if model_config.get('text_to_speech') else None
        self.more_like_this = json.dumps(model_config['more_like_this'], ensure_ascii=False) \
            if model_config.get('more_like_this') else None
        self.sensitive_word_avoidance = json.dumps(model_config['sensitive_word_avoidance'], ensure_ascii=False) \
            if model_config.get('sensitive_word_avoidance') else None
        self.external_data_tools = json.dumps(model_config['external_data_tools'], ensure_ascii=False) \
            if model_config.get('external_data_tools') else None
        self.model = json.dumps(model_config['model'], ensure_ascii=False) \
            if model_config.get('model') else None
        self.user_input_form = json.dumps(model_config['user_input_form'], ensure_ascii=False) \
            if model_config.get('user_input_form') else None
        self.dataset_query_variable = model_config.get('dataset_query_variable')
        self.pre_prompt = model_config['pre_prompt']
        self.agent_mode = json.dumps(model_config['agent_mode'], ensure_ascii=False) \
            if model_config.get('agent_mode') else None
        self.retriever_resource = json.dumps(model_config['retriever_resource'], ensure_ascii=False) \
            if model_config.get('retriever_resource') else None
        self.prompt_type = model_config.get('prompt_type', 'simple')
        self.chat_prompt_config = json.dumps(model_config.get('chat_prompt_config'), ensure_ascii=False) \
            if model_config.get('chat_prompt_config') else None
        self.completion_prompt_config = json.dumps(model_config.get('completion_prompt_config'), ensure_ascii=False) \
            if model_config.get('completion_prompt_config') else None
        self.dataset_configs = json.dumps(model_config.get('dataset_configs'), ensure_ascii=False) \
            if model_config.get('dataset_configs') else None
        self.file_upload = json.dumps(model_config.get('file_upload'), ensure_ascii=False) \
            if model_config.get('file_upload') else None
        return self

    def copy(self):
        new_app_model_config = AppModelConfig(
            id=self.id,
            app_id=self.app_id,
            opening_statement=self.opening_statement,
            suggested_questions=self.suggested_questions,
            suggested_questions_after_answer=self.suggested_questions_after_answer,
            speech_to_text=self.speech_to_text,
            text_to_speech=self.text_to_speech,
            more_like_this=self.more_like_this,
            sensitive_word_avoidance=self.sensitive_word_avoidance,
            external_data_tools=self.external_data_tools,
            model=self.model,
            user_input_form=self.user_input_form,
            dataset_query_variable=self.dataset_query_variable,
            pre_prompt=self.pre_prompt,
            agent_mode=self.agent_mode,
            retriever_resource=self.retriever_resource,
            prompt_type=self.prompt_type,
            chat_prompt_config=self.chat_prompt_config,
            completion_prompt_config=self.completion_prompt_config,
            dataset_configs=self.dataset_configs,
            file_upload=self.file_upload
        )

        return new_app_model_config


class InstalledApp(db.Model):
    __tablename__ = 'installed_apps'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='installed_app_pkey'),
        db.Index('installed_app_tenant_id_idx', 'tenant_id'),
        db.Index('installed_app_app_id_idx', 'app_id'),
        db.UniqueConstraint('tenant_id', 'app_id', name='unique_tenant_app')
    )

    id = db.Column(StringUUID, server_default=db.text('uuid_generate_v4()'))
    tenant_id = db.Column(StringUUID, nullable=False)
    app_id = db.Column(StringUUID, nullable=False)
    app_owner_tenant_id = db.Column(StringUUID, nullable=False)
    position = db.Column(db.Integer, nullable=False, default=0)
    is_pinned = db.Column(db.Boolean, nullable=False, server_default=db.text('false'))
    last_used_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))

    @property
    def app(self):
        app = db.session.query(App).filter(App.id == self.app_id).first()
        return app

    @property
    def tenant(self):
        tenant = db.session.query(Tenant).filter(Tenant.id == self.tenant_id).first()
        return tenant


class RecommendedApp(db.Model):
    __tablename__ = 'recommended_apps'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='recommended_app_pkey'),
        db.Index('recommended_app_app_id_idx', 'app_id'),
        db.Index('recommended_app_is_listed_idx', 'is_listed', 'language')
    )

    id = db.Column(StringUUID, primary_key=True, server_default=db.text('uuid_generate_v4()'))
    app_id = db.Column(StringUUID, nullable=False)
    description = db.Column(db.JSON, nullable=False)
    copyright = db.Column(db.String(255), nullable=False)
    privacy_policy = db.Column(db.String(255), nullable=False)
    custom_disclaimer = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(255), nullable=False)
    position = db.Column(db.Integer, nullable=False, default=0)
    is_listed = db.Column(db.Boolean, nullable=False, default=True)
    install_count = db.Column(db.Integer, nullable=False, default=0)
    language = db.Column(db.String(255), nullable=False, server_default=db.text("'en-US'::character varying"))
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))

    @property
    def app(self):
        app = db.session.query(App).filter(App.id == self.app_id).first()
        return app
