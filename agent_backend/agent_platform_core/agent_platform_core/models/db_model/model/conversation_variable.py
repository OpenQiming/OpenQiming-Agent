import json

from sqlalchemy import func
from sqlalchemy.orm import Mapped

from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID
from agent_platform_core.factories import variable_factory
from agent_platform_core.variables import Variable


class ConversationVariable(db.Model):
    __tablename__ = "workflow_conversation_variables"

    id: Mapped[str] = db.Column(StringUUID, primary_key=True)
    conversation_id: Mapped[str] = db.Column(StringUUID, nullable=False, primary_key=True)
    app_id: Mapped[str] = db.Column(StringUUID, nullable=False, index=True)
    data = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.text("CURRENT_TIMESTAMP(0)"))
    updated_at = db.Column(
        db.DateTime, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp()
    )

    def __init__(self, *, id: str, app_id: str, conversation_id: str, data: str) -> None:
        self.id = id
        self.app_id = app_id
        self.conversation_id = conversation_id
        self.data = data

    @classmethod
    def from_variable(cls, *, app_id: str, conversation_id: str, variable: Variable) -> "ConversationVariable":
        obj = cls(
            id=variable.id,
            app_id=app_id,
            conversation_id=conversation_id,
            data=variable.model_dump_json(),
        )
        return obj

    def to_variable(self) -> Variable:
        mapping = json.loads(self.data)
        return variable_factory.build_conversation_variable_from_mapping(mapping)