import json
import re
from typing import Mapping, Any, Optional

from sqlalchemy.orm import mapped_column, Mapped

from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID
from agent_platform_core.file import FILE_MODEL_IDENTITY, File
from agent_platform_core.file.tool_file_parser import ToolFileParser
from agent_platform_core.file import helpers as file_helpers
from agent_platform_core.models.db_model.model import App
from agent_platform_core.models.enum_model.app_mode import AppMode
from .app import AppModelConfig
from .app_annotation_hit_history import AppAnnotationHitHistory
from .dataset_retriever_resource import DatasetRetrieverResource
from .end_user import EndUser
from .message_agent_thought import MessageAgentThought
from .message_annotation import MessageAnnotation
from .message_feedback import MessageFeedback
from .message_file import MessageFile
from .upload_file import UploadFile

"""
@Date    ：2024/7/15 9:08 
@Version: 1.0
@Description:

"""


class Conversation(db.Model):
    __tablename__ = "conversations"
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="conversation_pkey"),
        db.Index("conversation_app_from_user_idx", "app_id", "from_source", "from_end_user_id"),
    )

    id = db.Column(StringUUID, server_default=db.text("uuid_generate_v4()"))
    app_id = db.Column(StringUUID, nullable=False)
    app_model_config_id = db.Column(StringUUID, nullable=True)
    model_provider = db.Column(db.String(255), nullable=True)
    override_model_configs = db.Column(db.Text)
    model_id = db.Column(db.String(255), nullable=True)
    mode = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    summary = db.Column(db.Text)
    _inputs: Mapped[dict] = mapped_column("inputs", db.JSON)
    introduction = db.Column(db.Text)
    system_instruction = db.Column(db.Text)
    system_instruction_tokens = db.Column(db.Integer, nullable=False, server_default=db.text("0"))
    status = db.Column(db.String(255), nullable=False)
    invoke_from = db.Column(db.String(255), nullable=True)
    from_source = db.Column(db.String(255), nullable=False)
    from_end_user_id = db.Column(StringUUID)
    from_account_id = db.Column(StringUUID)
    read_at = db.Column(db.DateTime)
    read_account_id = db.Column(StringUUID)
    dialogue_count: Mapped[int] = mapped_column(default=0)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP(0)"))
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP(0)"))

    messages = db.relationship("Message", backref="conversation", lazy="select", passive_deletes="all")
    message_annotations = db.relationship(
        "MessageAnnotation", backref="conversation", lazy="select", passive_deletes="all"
    )

    is_deleted = db.Column(db.Boolean, nullable=False, server_default=db.text("false"))

    @property
    def inputs(self):
        inputs = self._inputs.copy()
        for key, value in inputs.items():
            if isinstance(value, dict) and value.get("agent_platform_model_identity") == FILE_MODEL_IDENTITY:
                inputs[key] = File.model_validate(value)
            elif isinstance(value, list) and all(
                isinstance(item, dict) and item.get("agent_platform_model_identity") == FILE_MODEL_IDENTITY for item in value
            ):
                inputs[key] = [File.model_validate(item) for item in value]
        return inputs

    @inputs.setter
    def inputs(self, value: Mapping[str, Any]):
        inputs = dict(value)
        for k, v in inputs.items():
            if isinstance(v, File):
                inputs[k] = v.model_dump()
            elif isinstance(v, list) and all(isinstance(item, File) for item in v):
                inputs[k] = [item.model_dump() for item in v]
        self._inputs = inputs

    @property
    def model_config(self):
        model_config = {}
        if self.mode == AppMode.ADVANCED_CHAT.value:
            if self.override_model_configs:
                override_model_configs = json.loads(self.override_model_configs)
                model_config = override_model_configs
        else:
            if self.override_model_configs:
                override_model_configs = json.loads(self.override_model_configs)

                if "model" in override_model_configs:
                    app_model_config = AppModelConfig()
                    app_model_config = app_model_config.from_model_config_dict(override_model_configs)
                    model_config = app_model_config.to_dict()
                else:
                    model_config["configs"] = override_model_configs
            else:
                app_model_config = (
                    db.session.query(AppModelConfig).filter(AppModelConfig.id == self.app_model_config_id).first()
                )
                if app_model_config:
                    model_config = app_model_config.to_dict()

        model_config["model_id"] = self.model_id
        model_config["provider"] = self.model_provider

        return model_config

    @property
    def summary_or_query(self):
        if self.summary:
            return self.summary
        else:
            first_message = self.first_message
            if first_message:
                return first_message.query
            else:
                return ""

    @property
    def annotated(self):
        return db.session.query(MessageAnnotation).filter(MessageAnnotation.conversation_id == self.id).count() > 0

    @property
    def annotation(self):
        return db.session.query(MessageAnnotation).filter(MessageAnnotation.conversation_id == self.id).first()

    @property
    def message_count(self):
        return db.session.query(Message).filter(Message.conversation_id == self.id).count()

    @property
    def user_feedback_stats(self):
        like = (
            db.session.query(MessageFeedback)
            .filter(
                MessageFeedback.conversation_id == self.id,
                MessageFeedback.from_source == "user",
                MessageFeedback.rating == "like",
            )
            .count()
        )

        dislike = (
            db.session.query(MessageFeedback)
            .filter(
                MessageFeedback.conversation_id == self.id,
                MessageFeedback.from_source == "user",
                MessageFeedback.rating == "dislike",
            )
            .count()
        )

        return {"like": like, "dislike": dislike}

    @property
    def admin_feedback_stats(self):
        like = (
            db.session.query(MessageFeedback)
            .filter(
                MessageFeedback.conversation_id == self.id,
                MessageFeedback.from_source == "admin",
                MessageFeedback.rating == "like",
            )
            .count()
        )

        dislike = (
            db.session.query(MessageFeedback)
            .filter(
                MessageFeedback.conversation_id == self.id,
                MessageFeedback.from_source == "admin",
                MessageFeedback.rating == "dislike",
            )
            .count()
        )

        return {"like": like, "dislike": dislike}

    @property
    def first_message(self):
        return db.session.query(Message).filter(Message.conversation_id == self.id).first()

    @property
    def app(self):
        return db.session.query(App).filter(App.id == self.app_id).first()

    @property
    def from_end_user_session_id(self):
        if self.from_end_user_id:
            end_user = db.session.query(EndUser).filter(EndUser.id == self.from_end_user_id).first()
            if end_user:
                return end_user.session_id

        return None

    @property
    def in_debug_mode(self):
        return self.override_model_configs is not None


class Message(db.Model):
    __tablename__ = "messages"
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="message_pkey"),
        db.Index("message_app_id_idx", "app_id", "created_at"),
        db.Index("message_conversation_id_idx", "conversation_id"),
        db.Index("message_end_user_idx", "app_id", "from_source", "from_end_user_id"),
        db.Index("message_account_idx", "app_id", "from_source", "from_account_id"),
        db.Index("message_workflow_run_id_idx", "conversation_id", "workflow_run_id"),
        db.Index("message_created_at_idx", "created_at"),
    )

    id = db.Column(StringUUID, server_default=db.text("uuid_generate_v4()"))
    app_id = db.Column(StringUUID, nullable=False)
    model_provider = db.Column(db.String(255), nullable=True)
    model_id = db.Column(db.String(255), nullable=True)
    override_model_configs = db.Column(db.Text)
    conversation_id = db.Column(StringUUID, db.ForeignKey("conversations.id"), nullable=False)
    _inputs: Mapped[dict] = mapped_column("inputs", db.JSON)
    query: Mapped[str] = db.Column(db.Text, nullable=False)
    message = db.Column(db.JSON, nullable=False)
    message_tokens = db.Column(db.Integer, nullable=False, server_default=db.text("0"))
    message_unit_price = db.Column(db.Numeric(10, 4), nullable=False)
    message_price_unit = db.Column(db.Numeric(10, 7), nullable=False, server_default=db.text("0.001"))
    answer: Mapped[str] = db.Column(db.Text, nullable=False)
    answer_tokens = db.Column(db.Integer, nullable=False, server_default=db.text("0"))
    answer_unit_price = db.Column(db.Numeric(10, 4), nullable=False)
    answer_price_unit = db.Column(db.Numeric(10, 7), nullable=False, server_default=db.text("0.001"))
    parent_message_id = db.Column(StringUUID, nullable=True)
    provider_response_latency = db.Column(db.Float, nullable=False, server_default=db.text("0"))
    total_price = db.Column(db.Numeric(10, 7))
    currency = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255), nullable=False, server_default=db.text("'normal'::character varying"))
    error = db.Column(db.Text)
    message_metadata = db.Column(db.Text)
    invoke_from: Mapped[Optional[str]] = db.Column(db.String(255), nullable=True)
    from_source = db.Column(db.String(255), nullable=False)
    from_end_user_id: Mapped[Optional[str]] = db.Column(StringUUID)
    from_account_id: Mapped[Optional[str]] = db.Column(StringUUID)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP(0)"))
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP(0)"))
    agent_based = db.Column(db.Boolean, nullable=False, server_default=db.text("false"))
    workflow_run_id = db.Column(StringUUID)

    @property
    def inputs(self):
        inputs = self._inputs.copy()
        for key, value in inputs.items():
            if isinstance(value, dict) and value.get("agent_platform_model_identity") == FILE_MODEL_IDENTITY:
                inputs[key] = File.model_validate(value)
            elif isinstance(value, list) and all(
                isinstance(item, dict) and item.get("agent_platform_model_identity") == FILE_MODEL_IDENTITY for item in value
            ):
                inputs[key] = [File.model_validate(item) for item in value]
        return inputs

    @inputs.setter
    def inputs(self, value: Mapping[str, Any]):
        inputs = dict(value)
        for k, v in inputs.items():
            if isinstance(v, File):
                inputs[k] = v.model_dump()
            elif isinstance(v, list) and all(isinstance(item, File) for item in v):
                inputs[k] = [item.model_dump() for item in v]
        self._inputs = inputs

    @property
    def re_sign_file_url_answer(self) -> str:
        if not self.answer:
            return self.answer

        pattern = r"\[!?.*?\]\((((http|https):\/\/.+)?\/files\/(tools\/)?[\w-]+.*?timestamp=.*&nonce=.*&sign=.*)\)"
        matches = re.findall(pattern, self.answer)

        if not matches:
            return self.answer

        urls = [match[0] for match in matches]

        # remove duplicate urls
        urls = list(set(urls))

        if not urls:
            return self.answer

        re_sign_file_url_answer = self.answer
        for url in urls:
            if "files/tools" in url:
                # get tool file id
                tool_file_id_pattern = r"\/files\/tools\/([\.\w-]+)?\?timestamp="
                result = re.search(tool_file_id_pattern, url)
                if not result:
                    continue

                tool_file_id = result.group(1)

                # get extension
                if "." in tool_file_id:
                    split_result = tool_file_id.split(".")
                    extension = f".{split_result[-1]}"
                    if len(extension) > 10:
                        extension = ".bin"
                    tool_file_id = split_result[0]
                else:
                    extension = ".bin"

                if not tool_file_id:
                    continue

                sign_url = ToolFileParser.get_tool_file_manager().sign_file(
                    tool_file_id=tool_file_id, extension=extension
                )
            elif "file-preview" in url:
                # get upload file id
                upload_file_id_pattern = r"\/files\/([\w-]+)\/file-preview?\?timestamp="
                result = re.search(upload_file_id_pattern, url)
                if not result:
                    continue

                upload_file_id = result.group(1)
                if not upload_file_id:
                    continue
                sign_url = file_helpers.get_signed_file_url(upload_file_id)
            elif "image-preview" in url:
                # image-preview is deprecated, use file-preview instead
                upload_file_id_pattern = r"\/files\/([\w-]+)\/image-preview?\?timestamp="
                result = re.search(upload_file_id_pattern, url)
                if not result:
                    continue
                upload_file_id = result.group(1)
                if not upload_file_id:
                    continue
                sign_url = file_helpers.get_signed_file_url(upload_file_id)
            else:
                continue

            re_sign_file_url_answer = re_sign_file_url_answer.replace(url, sign_url)

        return re_sign_file_url_answer

    @property
    def user_feedback(self):
        feedback = (
            db.session.query(MessageFeedback)
            .filter(MessageFeedback.message_id == self.id, MessageFeedback.from_source == "user")
            .first()
        )
        return feedback

    @property
    def admin_feedback(self):
        feedback = (
            db.session.query(MessageFeedback)
            .filter(MessageFeedback.message_id == self.id, MessageFeedback.from_source == "admin")
            .first()
        )
        return feedback

    @property
    def feedbacks(self):
        feedbacks = db.session.query(MessageFeedback).filter(MessageFeedback.message_id == self.id).all()
        return feedbacks

    @property
    def annotation(self):
        annotation = db.session.query(MessageAnnotation).filter(MessageAnnotation.message_id == self.id).first()
        return annotation

    @property
    def annotation_hit_history(self):
        annotation_history = (
            db.session.query(AppAnnotationHitHistory).filter(AppAnnotationHitHistory.message_id == self.id).first()
        )
        if annotation_history:
            annotation = (
                db.session.query(MessageAnnotation)
                .filter(MessageAnnotation.id == annotation_history.annotation_id)
                .first()
            )
            return annotation
        return None

    @property
    def app_model_config(self):
        conversation = db.session.query(Conversation).filter(Conversation.id == self.conversation_id).first()
        if conversation:
            return (
                db.session.query(AppModelConfig).filter(AppModelConfig.id == conversation.app_model_config_id).first()
            )

        return None

    @property
    def in_debug_mode(self):
        return self.override_model_configs is not None

    @property
    def message_metadata_dict(self) -> dict:
        return json.loads(self.message_metadata) if self.message_metadata else {}

    @property
    def agent_thoughts(self):
        return (
            db.session.query(MessageAgentThought)
            .filter(MessageAgentThought.message_id == self.id)
            .order_by(MessageAgentThought.position.asc())
            .all()
        )

    @property
    def retriever_resources(self):
        return (
            db.session.query(DatasetRetrieverResource)
            .filter(DatasetRetrieverResource.message_id == self.id)
            .order_by(DatasetRetrieverResource.position.asc())
            .all()
        )

    @property
    def message_files(self):
        from agent_platform_core.factories import file_factory

        message_files = db.session.query(MessageFile).filter(MessageFile.message_id == self.id).all()
        current_app = db.session.query(App).filter(App.id == self.app_id).first()
        if not current_app:
            raise ValueError(f"App {self.app_id} not found")

        files: list[File] = []
        for message_file in message_files:
            if message_file.transfer_method == "local_file":
                if message_file.upload_file_id is None:
                    raise ValueError(f"MessageFile {message_file.id} is a local file but has no upload_file_id")
                file = file_factory.build_from_mapping(
                    mapping={
                        "id": message_file.id,
                        "upload_file_id": message_file.upload_file_id,
                        "transfer_method": message_file.transfer_method,
                        "type": message_file.type,
                    },
                    tenant_id=current_app.tenant_id,
                )
            elif message_file.transfer_method == "remote_url":
                if message_file.url is None:
                    raise ValueError(f"MessageFile {message_file.id} is a remote url but has no url")
                file = file_factory.build_from_mapping(
                    mapping={
                        "id": message_file.id,
                        "type": message_file.type,
                        "transfer_method": message_file.transfer_method,
                        "url": message_file.url,
                    },
                    tenant_id=current_app.tenant_id,
                )
            elif message_file.transfer_method == "tool_file":
                if message_file.upload_file_id is None:
                    assert message_file.url is not None
                    message_file.upload_file_id = message_file.url.split("/")[-1].split(".")[0]
                mapping = {
                    "id": message_file.id,
                    "type": message_file.type,
                    "transfer_method": message_file.transfer_method,
                    "tool_file_id": message_file.upload_file_id,
                }
                file = file_factory.build_from_mapping(
                    mapping=mapping,
                    tenant_id=current_app.tenant_id,
                )
            else:
                raise ValueError(
                    f"MessageFile {message_file.id} has an invalid transfer_method {message_file.transfer_method}"
                )
            files.append(file)

        result = [
            {"belongs_to": message_file.belongs_to, **file.to_dict()}
            for (file, message_file) in zip(files, message_files)
        ]

        db.session.commit()
        return result

    @property
    def workflow_run(self):
        if self.workflow_run_id:
            from agent_platform_core.workflow import WorkflowRun

            return db.session.query(WorkflowRun).filter(WorkflowRun.id == self.workflow_run_id).first()

        return None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "app_id": self.app_id,
            "conversation_id": self.conversation_id,
            "inputs": self.inputs,
            "query": self.query,
            "message": self.message,
            "answer": self.answer,
            "status": self.status,
            "error": self.error,
            "message_metadata": self.message_metadata_dict,
            "from_source": self.from_source,
            "from_end_user_id": self.from_end_user_id,
            "from_account_id": self.from_account_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "agent_based": self.agent_based,
            "workflow_run_id": self.workflow_run_id,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data["id"],
            app_id=data["app_id"],
            conversation_id=data["conversation_id"],
            inputs=data["inputs"],
            query=data["query"],
            message=data["message"],
            answer=data["answer"],
            status=data["status"],
            error=data["error"],
            message_metadata=json.dumps(data["message_metadata"]),
            from_source=data["from_source"],
            from_end_user_id=data["from_end_user_id"],
            from_account_id=data["from_account_id"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            agent_based=data["agent_based"],
            workflow_run_id=data["workflow_run_id"],
        )
