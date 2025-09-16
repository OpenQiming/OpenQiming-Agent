from typing import Union

from agent_platform_core.async_model_manager import AsyncModelInstance

from agent_platform_core.app.entities.app_invoke_entities import ModelConfigWithCredentialsEntity
from agent_platform_core.model_manager import ModelInstance
from agent_platform_core.model_runtime.entities.message_entities import PromptMessageTool, SystemPromptMessage, \
    UserPromptMessage


class FunctionCallMultiDatasetRouter:

    async def invoke(
            self,
            query: str,
            dataset_tools: list[PromptMessageTool],
            model_config: ModelConfigWithCredentialsEntity,
            model_instance: AsyncModelInstance,

    ) -> Union[str, None]:
        """Given input, decided what to do.
        Returns:
            Action specifying what tool to use.
        """
        if len(dataset_tools) == 0:
            return None
        elif len(dataset_tools) == 1:
            return dataset_tools[0].name

        try:
            prompt_messages = [
                SystemPromptMessage(content='You are a helpful AI assistant.'),
                UserPromptMessage(content=query)
            ]
            result = await model_instance.invoke_llm(
                prompt_messages=prompt_messages,
                tools=dataset_tools,
                stream=False,
                model_parameters={
                    'temperature': 0.2,
                    'top_p': 0.3,
                    'max_tokens': 1500
                }
            )
            if result.message.tool_calls:
                # get retrieval model config
                return result.message.tool_calls[0].function.name
            return None
        except Exception as e:
            return None