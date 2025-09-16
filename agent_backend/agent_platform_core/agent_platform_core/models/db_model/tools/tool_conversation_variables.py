import json

from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID

"""
@Date    ：2024/7/15 9:01 
@Version: 1.0
@Description:

"""


class ToolConversationVariables(db.Model):
    """
    store the conversation variables from tool invoke
    """
    __tablename__ = "tool_conversation_variables"
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='tool_conversation_variables_pkey'),
        # add index for user_id and conversation_id
        db.Index('user_id_idx', 'user_id'),
        db.Index('conversation_id_idx', 'conversation_id'),
    )

    id = db.Column(StringUUID, server_default=db.text('uuid_generate_v4()'))
    # conversation user id
    user_id = db.Column(StringUUID, nullable=False)
    # tenant id
    tenant_id = db.Column(StringUUID, nullable=False)
    # conversation id
    conversation_id = db.Column(StringUUID, nullable=False)
    # variables pool
    variables_str = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))

    @property
    def variables(self) -> dict:
        return json.loads(self.variables_str)
