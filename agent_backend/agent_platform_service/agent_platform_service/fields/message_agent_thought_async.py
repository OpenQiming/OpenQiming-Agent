import json

from agent_platform_basic.extensions.ext_database import async_db
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from agent_platform_basic.libs import DbUtils
from agent_platform_core.models.db_model.model import MessageAgentThought


class MessageAgentThoughtAsync:
    def __init__(self,
                 session: AsyncSession = Depends(DbUtils.get_db_async_session)):
        self.session = session

    async def tools(self, msg:MessageAgentThought) -> list[str]:
        return msg.tool.split(',') if msg.tool else []

    async def tool_labels(self, agent_thought):
        try:
            if agent_thought.tool_labels_str:
                return json.loads(agent_thought.tool_labels_str)
            return {}
        except Exception as e:
            return {}

    async def tool_meta(self, agent_thought):
        try:
            if agent_thought.tool_meta_str:
                return json.loads(agent_thought.tool_meta_str)
            return {}
        except Exception as e:
            return {}

    async def tool_inputs_dict(self, agent_thought):
        tools = await self.tools(agent_thought)
        try:
            if agent_thought.tool_input:
                data = json.loads(agent_thought.tool_input)
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

    async def tool_outputs_dict(self, agent_thought: MessageAgentThought):
        tools = await self.tools(agent_thought)
        try:
            if agent_thought.observation:
                data = json.loads(agent_thought.observation)
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