import json
import time
from agent_platform_core.agent.cot_agent_runner import CotAgentRunner
from agent_platform_core.agent.llama_agent_runner import LlamaAgentRunner
from agent_platform_core.model_runtime.entities.message_entities import (
    AssistantPromptMessage,
    PromptMessage,
    SystemPromptMessage,
    TextPromptMessageContent,
    UserPromptMessage,
    IpythonPromptMessage,
)
from agent_platform_core.model_runtime.utils.encoders import jsonable_encoder


class LlamaChatAgentRunner(LlamaAgentRunner):
    def _organize_system_prompt(self) -> SystemPromptMessage:
        """
        Organize system prompt
        """
        prompt_entity = self.app_config.agent.prompt
        first_prompt = prompt_entity.first_prompt

        system_prompt = first_prompt \
            .replace("{{date}}", time.ctime()) \
            .replace("{{instruction}}", self._instruction) \
            .replace("{{tools}}", json.dumps(jsonable_encoder(self._prompt_messages_tools))) \
            .replace("{{tool_names}}", ', '.join([tool.name for tool in self._prompt_messages_tools]))

        return SystemPromptMessage(content=system_prompt)

    def _organize_user_query(self, query,  prompt_messages: list[PromptMessage] = None) -> list[PromptMessage]:
        """
        Organize user query
        """
        if self.files:
            prompt_message_contents = [TextPromptMessageContent(data=query)]
            for file_obj in self.files:
                prompt_message_contents.append(file_obj.prompt_message_content)

            prompt_messages.append(UserPromptMessage(content=prompt_message_contents))
        else:
            prompt_messages.append(UserPromptMessage(content=query))

        return prompt_messages

    def _organize_prompt_messages(self) -> list[PromptMessage]:
        """
        Organize
        """
        # organize system prompt
        system_message = self._organize_system_prompt()

        # organize current assistant messages
        agent_scratchpad = self._agent_scratchpad
        if not agent_scratchpad:
            assistant_messages = []
        else:
            assistant_message = AssistantPromptMessage(content='')
            ipython_message = IpythonPromptMessage(content='')
            for unit in agent_scratchpad:
                assistant_message.content += unit.agent_response
                ipython_message.content += unit.ipython

            assistant_messages = [assistant_message]
            ipython_messages = [ipython_message]

        # query messages
        query_messages = self._organize_user_query(self._query, [])

        if assistant_messages:
            # organize historic prompt messages
            historic_messages = self._organize_historic_prompt_messages([
                system_message,
                *query_messages,
                *assistant_messages,
                *ipython_messages,
            ])
            messages = [
                system_message,
                *historic_messages,
                *query_messages,
                *assistant_messages,
                *ipython_messages,
            ]
        else:
            # organize historic prompt messages
            historic_messages = self._organize_historic_prompt_messages_new()
            #historic_messages = self._organize_historic_prompt_messages([system_message, *query_messages])
            if historic_messages:
                if query_messages[-1] == historic_messages[-1]:
                    messages = [system_message, *historic_messages]
                else:
                    messages = [system_message, *historic_messages, *query_messages]
            else:
                messages = [system_message, *historic_messages, *query_messages]

        # join all messages
        return messages

    def _organize_historic_prompt_messages_new(self):
        history_prompt = []
        for message in self.history_prompt_messages:
            if isinstance(message, SystemPromptMessage):
                continue
            else:
                history_prompt.append(message)

        return history_prompt