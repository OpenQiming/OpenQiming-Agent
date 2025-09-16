import json
from typing import Any, Optional

from scipy.sparse import identity

from agent_platform_core.tools.__base.tool import Tool

from agent_platform_core.tools.__base.tool_runtime import ToolRuntime

from agent_platform_core.app.app_config.entities import DatasetRetrieveConfigEntity
from agent_platform_core.app.entities.app_invoke_entities import InvokeFrom
from agent_platform_core.callback_handler.async_index_tool_callback_handler import AsyncDatasetIndexToolCallbackHandler
from agent_platform_core.callback_handler.index_tool_callback_handler import DatasetIndexToolCallbackHandler
from agent_platform_core.rag.retrieval.dataset_retrieval import DatasetRetrieval
from agent_platform_core.tools.entities.common_entities import I18nObject
from agent_platform_core.tools.entities.tool_entities import (
    ToolDescription,
    ToolIdentity,
    ToolInvokeMessage,
    ToolParameter,
    ToolProviderType, ToolEntity,
)
from agent_platform_core.tools.tool.dataset_retriever.async_dataset_retriever_base_tool import \
    AsyncDatasetRetrieverBaseTool
from agent_platform_core.tools.tool.dataset_retriever.dataset_retriever_base_tool import DatasetRetrieverBaseTool
# from agent_platform_core.tools.tool.tool import Tool


class AsyncDatasetRetrieverTool(Tool):
    retrival_tool: AsyncDatasetRetrieverBaseTool

    def __init__(self, retrival_tool: AsyncDatasetRetrieverBaseTool, **data: Any):
        super().__init__(**data)
        self.retrival_tool = retrival_tool

    @staticmethod
    async def get_dataset_tools(tenant_id: str,
                          dataset_ids: list[str],
                          retrieve_config: DatasetRetrieveConfigEntity,
                          return_resource: bool,
                          invoke_from: InvokeFrom,
                          hit_callback: AsyncDatasetIndexToolCallbackHandler,
                          user_id: str,
                          inputs: dict,
                          ) -> list['AsyncDatasetRetrieverTool']:
        """
        get dataset tool
        """
        print("dataset_ids::::", dataset_ids)
        # check if retrieve_config is valid
        if dataset_ids is None or len(dataset_ids) == 0:
            return []
        if retrieve_config is None:
            return []

        feature = DatasetRetrieval()

        # save original retrieve strategy, and set retrieve strategy to SINGLE
        # Agent only support SINGLE mode
        original_retriever_mode = retrieve_config.retrieve_strategy
        retrieve_config.retrieve_strategy = DatasetRetrieveConfigEntity.RetrieveStrategy.SINGLE
        retrival_tools = await feature.async_to_dataset_retriever_tool(
            tenant_id=tenant_id,
            dataset_ids=dataset_ids,
            retrieve_config=retrieve_config,
            return_resource=return_resource,
            invoke_from=invoke_from,
            hit_callback=hit_callback,
            user_id=user_id,
            inputs=inputs,
        )
        if retrival_tools is None or len(retrival_tools) == 0:
            return []

        # restore retrieve strategy
        retrieve_config.retrieve_strategy = original_retriever_mode

        # convert retrival tools to Tools
        tools = []
        for retrieval_tool in retrival_tools:
            tool = AsyncDatasetRetrieverTool(
                retrival_tool=retrieval_tool,
                entity=ToolEntity(
                    identity=ToolIdentity(
                        provider="", author="", name=retrieval_tool.name, label=I18nObject(en_US="", zh_Hans="")
                    ),
                    parameters=[],
                    description=ToolDescription(human=I18nObject(en_US="", zh_Hans=""), llm=retrieval_tool.description),
                ),
                runtime=ToolRuntime(tenant_id=tenant_id),
            )

            tools.append(tool)

        return tools

    def get_runtime_parameters(self,
       conversation_id: Optional[str] = None,
        app_id: Optional[str] = None,
        message_id: Optional[str] = None,) -> list[ToolParameter]:
        return [
            ToolParameter(name='query',
                          label=I18nObject(en_US='', zh_Hans=''),
                          human_description=I18nObject(en_US='', zh_Hans=''),
                          type=ToolParameter.ToolParameterType.STRING,
                          form=ToolParameter.ToolParameterForm.LLM,
                          llm_description='Query for the dataset to be used to retrieve the dataset.',
                          required=True,
                          default='', placeholder=I18nObject(en_US="", zh_Hans="")),
        ]
    
    def tool_provider_type(self) -> ToolProviderType:
        return ToolProviderType.DATASET_RETRIEVAL

    def _invoke(self,
        user_id: str,
        tool_parameters: dict[str, Any],
        conversation_id: Optional[str] = None,
        app_id: Optional[str] = None,
        message_id: Optional[str] = None,) -> ToolInvokeMessage | list[ToolInvokeMessage]:
        """
        invoke dataset retriever tool
        """
        query = tool_parameters.get('query')
        if not query:
            return self.create_text_message(text='please input query')

        # invoke dataset retriever tool
        result = self.retrival_tool._run(query=query)

        return self.create_text_message(text=result)

    async def async_invoke(self,
        user_id: str,
        tool_parameters: dict[str, Any],
        conversation_id: Optional[str] = None,
        app_id: Optional[str] = None,
        message_id: Optional[str] = None,) -> ToolInvokeMessage | list[ToolInvokeMessage]:

        query = tool_parameters.get('query')
        print("query::::", query)
        if not query:
            return self.create_text_message(text='please input query')

        # invoke dataset retriever tool
        result = await self.retrival_tool._async_run(query=query)
        print('result::::', result)
        x = {
            "message": result
        }

        messagelist = []
        messagelist.append(self.create_text_message(result))
        messagelist.append(self.create_text_message(result))

        return messagelist

    def validate_credentials(self, credentials: dict[str, Any], parameters: dict[str, Any]) -> None:
        """
        validate the credentials for dataset retriever tool
        """
        pass
