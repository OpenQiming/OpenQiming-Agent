import json

from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID

"""
@Date    ：2024/7/15 9:30 
@Version: 1.0
@Description:

"""


class MessageAgentThought(db.Model):
    __tablename__ = 'message_agent_thoughts'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='message_agent_thought_pkey'),
        db.Index('message_agent_thought_message_id_idx', 'message_id'),
        db.Index('message_agent_thought_message_chain_id_idx', 'message_chain_id'),
    )

    id = db.Column(StringUUID, nullable=False, server_default=db.text('uuid_generate_v4()'))
    message_id = db.Column(StringUUID, nullable=False)
    message_chain_id = db.Column(StringUUID, nullable=True)
    position = db.Column(db.Integer, nullable=False)
    thought = db.Column(db.Text, nullable=True)
    tool = db.Column(db.Text, nullable=True)
    tool_labels_str = db.Column(db.Text, nullable=False, server_default=db.text("'{}'::text"))
    tool_meta_str = db.Column(db.Text, nullable=False, server_default=db.text("'{}'::text"))
    tool_input = db.Column(db.Text, nullable=True)
    observation = db.Column(db.Text, nullable=True)
    # plugin_id = db.Column(StringUUID, nullable=True)  ## for future design
    tool_process_data = db.Column(db.Text, nullable=True)
    message = db.Column(db.Text, nullable=True)
    message_token = db.Column(db.Integer, nullable=True)
    message_unit_price = db.Column(db.Numeric, nullable=True)
    message_price_unit = db.Column(db.Numeric(10, 7), nullable=False, server_default=db.text('0.001'))
    message_files = db.Column(db.Text, nullable=True)
    answer = db.Column(db.Text, nullable=True)
    answer_token = db.Column(db.Integer, nullable=True)
    answer_unit_price = db.Column(db.Numeric, nullable=True)
    answer_price_unit = db.Column(db.Numeric(10, 7), nullable=False, server_default=db.text('0.001'))
    tokens = db.Column(db.Integer, nullable=True)
    total_price = db.Column(db.Numeric, nullable=True)
    currency = db.Column(db.String, nullable=True)
    latency = db.Column(db.Float, nullable=True)
    created_by_role = db.Column(db.String, nullable=False)
    created_by = db.Column(StringUUID, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())

    @property
    def files(self) -> list:
        if self.message_files:
            return json.loads(self.message_files)
        else:
            return []

    @property
    def tools(self) -> list[str]:
        return self.tool.split(";") if self.tool else []

    @property
    def tool_labels(self) -> dict:
        try:
            if self.tool_labels_str:
                return json.loads(self.tool_labels_str)
            else:
                return {}
        except Exception as e:
            return {}

    @property
    def tool_meta(self) -> dict:
        try:
            if self.tool_meta_str:
                return json.loads(self.tool_meta_str)
            else:
                return {}
        except Exception as e:
            return {}

    @property
    def tool_inputs_dict(self) -> dict:
        tools = self.tools
        try:
            if self.tool_input:
                data = json.loads(self.tool_input)
                result = {}
                for tool in tools:
                    if tool in data:
                        result[tool] = data[tool]
                    else:
                        if len(tools) == 1:
                            result[tool] = data
                        else:
                            result[tool] = {}
                return result
            else:
                return {
                    tool: {} for tool in tools
                }
        except Exception as e:
            return {}

    @property
    def tool_outputs_dict(self) -> dict:
        tools = self.tools
        try:
            if self.observation:
                data = json.loads(self.observation)
                result = {}
                for tool in tools:
                    if tool in data:
                        result[tool] = data[tool]
                    else:
                        if len(tools) == 1:
                            result[tool] = data
                        else:
                            result[tool] = {}
                return result
            else:
                return {
                    tool: {} for tool in tools
                }
        except Exception as e:
            if self.observation:
                return {
                    tool: self.observation for tool in tools
                }
