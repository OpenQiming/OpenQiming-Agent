from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID

"""
@Date    ：2024/7/15 9:01 
@Version: 1.0
@Description:

"""


class ToolModelInvoke(db.Model):
    """
    store the invoke logs from tool invoke
    """
    __tablename__ = "tool_model_invokes"
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='tool_model_invoke_pkey'),
    )

    id = db.Column(StringUUID, server_default=db.text('uuid_generate_v4()'))
    # who invoke this tool
    user_id = db.Column(StringUUID, nullable=False)
    # tenant id
    tenant_id = db.Column(StringUUID, nullable=False)
    # provider
    provider = db.Column(db.String(40), nullable=False)
    # type
    tool_type = db.Column(db.String(40), nullable=False)
    # tool name
    tool_name = db.Column(db.String(40), nullable=False)
    # invoke parameters
    model_parameters = db.Column(db.Text, nullable=False)
    # prompt messages
    prompt_messages = db.Column(db.Text, nullable=False)
    # invoke response
    model_response = db.Column(db.Text, nullable=False)

    prompt_tokens = db.Column(db.Integer, nullable=False, server_default=db.text('0'))
    answer_tokens = db.Column(db.Integer, nullable=False, server_default=db.text('0'))
    answer_unit_price = db.Column(db.Numeric(10, 4), nullable=False)
    answer_price_unit = db.Column(db.Numeric(10, 7), nullable=False, server_default=db.text('0.001'))
    provider_response_latency = db.Column(db.Float, nullable=False, server_default=db.text('0'))
    total_price = db.Column(db.Numeric(10, 7))
    currency = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
