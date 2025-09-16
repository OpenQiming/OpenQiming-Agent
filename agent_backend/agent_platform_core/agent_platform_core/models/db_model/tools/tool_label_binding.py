from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID

"""
@Date    ：2024/7/15 8:59 
@Version: 1.0
@Description:

"""


class ToolLabelBinding(db.Model):
    """
    The table stores the labels for tools.
    """
    __tablename__ = 'tool_label_bindings'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='tool_label_bind_pkey'),
        db.UniqueConstraint('tool_id', 'label_name', name='unique_tool_label_bind'),
    )

    id = db.Column(StringUUID, server_default=db.text('uuid_generate_v4()'))
    # tool id
    tool_id = db.Column(db.String(64), nullable=False)
    # tool type
    tool_type = db.Column(db.String(40), nullable=False)
    # label name
    label_name = db.Column(db.String(40), nullable=False)
