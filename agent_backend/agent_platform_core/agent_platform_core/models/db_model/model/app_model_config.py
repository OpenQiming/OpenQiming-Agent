import json

from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID
from .app import App
from .app_annotation_setting import AppAnnotationSetting

"""
@Date    ：2024/7/14 23:54 
@Version: 1.0
@Description:

"""

class AppModelConfig(db.Model):
    __tablename__ = 'app_model_configs'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='app_model_config_pkey'),
        db.Index('app_app_id_idx', 'app_id')
    )

    id = db.Column(StringUUID, server_default=db.text('uuid_generate_v4()'))
    app_id = db.Column(StringUUID, nullable=False)
    provider = db.Column(db.String(255), nullable=True)
    model_id = db.Column(db.String(255), nullable=True)
    configs = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
    opening_statement = db.Column(db.Text)
    suggested_questions = db.Column(db.Text)
    suggested_questions_after_answer = db.Column(db.Text)
    speech_to_text = db.Column(db.Text)
    text_to_speech = db.Column(db.Text)
    more_like_this = db.Column(db.Text)
    model = db.Column(db.Text)
    user_input_form = db.Column(db.Text)
    dataset_query_variable = db.Column(db.String(255))
    pre_prompt = db.Column(db.Text)
    agent_mode = db.Column(db.Text)
    sensitive_word_avoidance = db.Column(db.Text)
    retriever_resource = db.Column(db.Text)
    prompt_type = db.Column(db.String(255), nullable=False, server_default=db.text("'simple'::character varying"))
    chat_prompt_config = db.Column(db.Text)
    completion_prompt_config = db.Column(db.Text)
    dataset_configs = db.Column(db.Text)
    external_data_tools = db.Column(db.Text)
    file_upload = db.Column(db.Text)

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
            "annotation_reply": self.annotation_reply_dict,
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
        self.suggested_questions = json.dumps(model_config['suggested_questions']) \
            if model_config.get('suggested_questions') else None
        self.suggested_questions_after_answer = json.dumps(model_config['suggested_questions_after_answer']) \
            if model_config.get('suggested_questions_after_answer') else None
        self.speech_to_text = json.dumps(model_config['speech_to_text']) \
            if model_config.get('speech_to_text') else None
        self.text_to_speech = json.dumps(model_config['text_to_speech']) \
            if model_config.get('text_to_speech') else None
        self.more_like_this = json.dumps(model_config['more_like_this']) \
            if model_config.get('more_like_this') else None
        self.sensitive_word_avoidance = json.dumps(model_config['sensitive_word_avoidance']) \
            if model_config.get('sensitive_word_avoidance') else None
        self.external_data_tools = json.dumps(model_config['external_data_tools']) \
            if model_config.get('external_data_tools') else None
        self.model = json.dumps(model_config['model']) \
            if model_config.get('model') else None
        self.user_input_form = json.dumps(model_config['user_input_form']) \
            if model_config.get('user_input_form') else None
        self.dataset_query_variable = model_config.get('dataset_query_variable')
        self.pre_prompt = model_config['pre_prompt']
        self.agent_mode = json.dumps(model_config['agent_mode']) \
            if model_config.get('agent_mode') else None
        self.retriever_resource = json.dumps(model_config['retriever_resource']) \
            if model_config.get('retriever_resource') else None
        self.prompt_type = model_config.get('prompt_type', 'simple')
        self.chat_prompt_config = json.dumps(model_config.get('chat_prompt_config')) \
            if model_config.get('chat_prompt_config') else None
        self.completion_prompt_config = json.dumps(model_config.get('completion_prompt_config')) \
            if model_config.get('completion_prompt_config') else None
        self.dataset_configs = json.dumps(model_config.get('dataset_configs')) \
            if model_config.get('dataset_configs') else None
        self.file_upload = json.dumps(model_config.get('file_upload')) \
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

