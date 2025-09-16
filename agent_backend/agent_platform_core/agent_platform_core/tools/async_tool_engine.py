import json
import traceback
from collections.abc import Mapping
from copy import deepcopy
from datetime import datetime
from mimetypes import guess_type
from typing import Any, Optional, Union

from yarl import URL

from agent_platform_core.app.entities.app_invoke_entities import InvokeFrom
from agent_platform_core.callback_handler.agent_tool_callback_handler import AgentPlatformAgentCallbackHandler
from agent_platform_core.callback_handler.workflow_tool_callback_handler import AgentPlatformWorkflowCallbackHandler
from agent_platform_core.file import FileType
from agent_platform_core.file.models import FileTransferMethod
from agent_platform_core.ops.ops_trace_manager import TraceQueueManager
from agent_platform_core.tools.entities.tool_entities import ToolInvokeMessage, ToolInvokeMessageBinary, ToolInvokeMeta, \
    ToolParameter, safe_model_dump
from agent_platform_core.tools.errors import (
    ToolEngineInvokeError,
    ToolInvokeError,
    ToolNotFoundError,
    ToolNotSupportedError,
    ToolParameterValidationError,
    ToolProviderCredentialValidationError,
    ToolProviderNotFoundError,
)
from agent_platform_core.tools.plugin_tool.tool import PluginTool
from agent_platform_core.tools.tool.async_dataset_retriever_tool import AsyncDatasetRetrieverTool
from agent_platform_core.tools.tool.tool import Tool
from agent_platform_core.tools.tool.workflow_tool import WorkflowTool
from agent_platform_core.tools.utils.async_message_transformer import AsyncToolFileMessageTransformer
from agent_platform_basic.extensions.ext_database import async_db
from agent_platform_core.models.enum_model.enums import CreatedByRole
from agent_platform_core.models.db_model.model import Message, MessageFile


class AsyncToolEngine:
    """
    Tool runtime engine take care of the tool executions.
    """

    @staticmethod
    async def agent_invoke(
        tool: Tool,
        tool_parameters: Union[str, dict],
        user_id: str,
        tenant_id: str,
        message: Message,
        invoke_from: InvokeFrom,
        agent_tool_callback: AgentPlatformAgentCallbackHandler,
        trace_manager: Optional[TraceQueueManager] = None,
    ) -> tuple[str, list[tuple[MessageFile, bool]], ToolInvokeMeta]:
        """
        Agent invokes the tool with the given arguments.
        """
        # check if arguments is a string
        if isinstance(tool_parameters, str):
            # check if this tool has only one parameter
            parameters = [
                parameter
                for parameter in tool.get_runtime_parameters()
                if parameter.form == ToolParameter.ToolParameterForm.LLM
            ]
            if parameters and len(parameters) == 1:
                tool_parameters = {parameters[0].name: tool_parameters}
            else:
                try:
                    tool_parameters = json.loads(tool_parameters)
                except Exception as e:
                    pass
                if not isinstance(tool_parameters, dict):
                    raise ValueError(f"tool_parameters should be a dict, but got a string: {tool_parameters}")

        # invoke the tool
        try:
            if hasattr(tool, "entity") and hasattr(tool.entity, "identity"):
                tool_name = tool.entity.identity.name
            else:
                tool_name = tool.identity.name
            print("tool:::xxxx", tool, tool_parameters)
            # hit the callback handler
            agent_tool_callback.on_tool_start(tool_name=tool_name, tool_inputs=tool_parameters)

            meta, response = await AsyncToolEngine._invoke(tool, tool_parameters, user_id)
            response = await AsyncToolFileMessageTransformer.transform_tool_invoke_messages(
                messages=response, user_id=user_id, tenant_id=tenant_id, conversation_id=message.conversation_id
            )

            # extract binary data from tool invoke message
            binary_files = AsyncToolEngine._extract_tool_response_binary(response)
            # create message file
            message_files = await AsyncToolEngine._create_message_files(
                tool_messages=binary_files, agent_message=message, invoke_from=invoke_from, user_id=user_id
            )

            plain_text = AsyncToolEngine._convert_tool_response_to_str(response)

            # hit the callback handler
            agent_tool_callback.on_tool_end(
                tool_name=tool_name,
                tool_inputs=tool_parameters,
                tool_outputs=plain_text,
                message_id=message.id,
                trace_manager=trace_manager,
            )

            # transform tool invoke message to get LLM friendly message
            return plain_text, message_files, meta
        except ToolProviderCredentialValidationError as e:
            error_response = "Please check your tool provider credentials"
            agent_tool_callback.on_tool_error(e)
        except (ToolNotFoundError, ToolNotSupportedError, ToolProviderNotFoundError) as e:
            error_response = f"there is not a tool named {tool.identity.name}"
            agent_tool_callback.on_tool_error(e)
        except ToolParameterValidationError as e:
            error_response = f"tool parameters validation error: {e}, please check your tool parameters"
            agent_tool_callback.on_tool_error(e)
        except ToolInvokeError as e:
            error_response = f"tool invoke error: {e}"
            agent_tool_callback.on_tool_error(e)
        except ToolEngineInvokeError as e:
            meta = e.args[0]
            error_response = f"tool invoke error: {meta.error}"
            agent_tool_callback.on_tool_error(e)
            return error_response, [], meta
        except Exception as e:
            print(traceback.format_exc())
            error_response = f"unknown error: {traceback.format_exc()}"
            agent_tool_callback.on_tool_error(e)

        return error_response, [], ToolInvokeMeta.error_instance(error_response)

    @staticmethod
    async def workflow_invoke(
        tool: Tool,
        tool_parameters: Mapping[str, Any],
        user_id: str,
        workflow_tool_callback: AgentPlatformWorkflowCallbackHandler,
        workflow_call_depth: int,
        semaphore_id: Optional[str] = None,
    ) -> list[ToolInvokeMessage]:
        """
        Workflow invokes the tool with the given arguments.
        """
        try:
            # hit the callback handler
            # assert tool.identity is not None
            if hasattr(tool, "entity") and hasattr(tool.entity, "identity"):
                tool_name = tool.entity.identity.name
            else:
                tool_name = tool.identity.name

            workflow_tool_callback.on_tool_start(tool_name=tool_name, tool_inputs=tool_parameters)

            if isinstance(tool, WorkflowTool):
                tool.workflow_call_depth = workflow_call_depth + 1
                tool.semaphore_id = semaphore_id

            if tool.runtime and tool.runtime.runtime_parameters:
                tool_parameters = {**tool.runtime.runtime_parameters, **tool_parameters}

            if isinstance(tool, PluginTool):
                response = tool.invoke(user_id=user_id, tool_parameters=tool_parameters)
            else:
                response = await tool.async_invoke(user_id=user_id, tool_parameters=tool_parameters)

            # hit the callback handler
            workflow_tool_callback.on_tool_end(
                tool_name=tool_name,
                tool_inputs=tool_parameters,
                tool_outputs=response,
            )

            return response
        except Exception as e:
            workflow_tool_callback.on_tool_error(e)
            raise e

    @staticmethod
    async def _invoke(tool: Tool, tool_parameters: dict, user_id: str) -> tuple[ToolInvokeMeta, list[ToolInvokeMessage]]:
        """
        Invoke the tool with the given arguments.
        """
        started_at = datetime.now()
        if hasattr(tool, "entity") and hasattr(tool.entity, "identity"):
            tool_name = tool.entity.identity.name
            tool_provider = tool.entity.identity.provider
            tool_provider_type = tool.tool_provider_type().value
            tool_icon = tool.entity.identity.icon
        else:
            tool_name = tool.identity.name
            tool_provider = tool.identity.provider
            tool_provider_type = tool.tool_provider_type().value
            tool_icon = tool.identity.icon

        meta = ToolInvokeMeta(
            time_cost=0.0,
            error=None,
            tool_config={
                "tool_name": tool_name,
                "tool_provider": tool_provider,
                "tool_provider_type": tool_provider_type,
                "tool_parameters": deepcopy(tool.runtime.runtime_parameters),
                "tool_icon": tool_icon,
            },
        )
        try:
            response = await tool.async_invoke(user_id=user_id, tool_parameters=tool_parameters)
        except Exception as e:
            meta.error = str(e)
            raise ToolEngineInvokeError(meta)
        finally:
            ended_at = datetime.now()
            meta.time_cost = (ended_at - started_at).total_seconds()
        print("response::::", response)
        return meta, response

    @staticmethod
    def _convert_tool_response_to_str(tool_response: list[ToolInvokeMessage]) -> str:
        """
        Handle tool response
        """
        result = ""
        for response in tool_response:
            if response.type == ToolInvokeMessage.MessageType.TEXT:
                result += response.message
            elif response.type == ToolInvokeMessage.MessageType.LINK:
                result += f"result link: {response.message}. please tell user to check it."
            elif response.type in {ToolInvokeMessage.MessageType.IMAGE_LINK, ToolInvokeMessage.MessageType.IMAGE}:
                result += (
                    "(图片已经由平台展示给用户，你无需再给用户展示) "
                    "The image which had been created and displyed to user on the platform already, "
                    "only tell the user to check it."
                    # "image has been created and sent to user already, you do not need to create it,"
                    # " just tell the user to check it now."
                )
            elif response.type == ToolInvokeMessage.MessageType.JSON:
                result += f"tool response: {json.dumps(safe_model_dump(response.message), ensure_ascii=False)}."
            else:
                result += f"tool response: {response.message}."

        return result

    @staticmethod
    def _extract_tool_response_binary(tool_response: list[ToolInvokeMessage]) -> list[ToolInvokeMessageBinary]:
        """
        Extract tool response binary
        """
        result = []

        for response in tool_response:
            if response.type in {ToolInvokeMessage.MessageType.IMAGE_LINK, ToolInvokeMessage.MessageType.IMAGE}:
                mimetype = None
                if response.meta.get("mime_type"):
                    mimetype = response.meta.get("mime_type")
                else:
                    try:
                        url = URL(response.message)
                        extension = url.suffix
                        guess_type_result, _ = guess_type(f"a{extension}")
                        if guess_type_result:
                            mimetype = guess_type_result
                    except Exception:
                        pass

                if not mimetype:
                    mimetype = "image/jpeg"

                result.append(
                    ToolInvokeMessageBinary(
                        mimetype=response.meta.get("mime_type", "image/jpeg"),
                        url=response.message,
                        save_as=response.save_as,
                    )
                )
            elif response.type == ToolInvokeMessage.MessageType.BLOB:
                result.append(
                    ToolInvokeMessageBinary(
                        mimetype=response.meta.get("mime_type", "octet/stream"),
                        url=response.message,
                        save_as=response.save_as,
                    )
                )
            elif response.type == ToolInvokeMessage.MessageType.LINK:
                # check if there is a mime type in meta
                if response.meta and "mime_type" in response.meta:
                    result.append(
                        ToolInvokeMessageBinary(
                            mimetype=response.meta.get("mime_type", "octet/stream")
                            if response.meta
                            else "octet/stream",
                            url=response.message,
                            save_as=response.save_as,
                        )
                    )

        return result

    @staticmethod
    async def _create_message_files(
        tool_messages: list[ToolInvokeMessageBinary],
        agent_message: Message,
        invoke_from: InvokeFrom,
        user_id: str,
    ) -> list[tuple[Any, str]]:
        """
        Create message file

        :param messages: messages
        :return: message files, should save as variable
        """
        result = []
        async with async_db.AsyncSessionLocal() as session:
            for message in tool_messages:
                if "image" in message.mimetype:
                    file_type = FileType.IMAGE
                elif "video" in message.mimetype:
                    file_type = FileType.VIDEO
                elif "audio" in message.mimetype:
                    file_type = FileType.AUDIO
                elif "text" in message.mimetype or "pdf" in message.mimetype:
                    file_type = FileType.DOCUMENT
                else:
                    file_type = FileType.CUSTOM

                # extract tool file id from url
                tool_file_id = message.url.split("/")[-1].split(".")[0]
                message_file = MessageFile(
                    message_id=agent_message.id,
                    type=file_type,
                    transfer_method=FileTransferMethod.TOOL_FILE,
                    belongs_to="assistant",
                    url=message.url,
                    upload_file_id=tool_file_id,
                    created_by_role=(
                        CreatedByRole.ACCOUNT
                        if invoke_from in {InvokeFrom.EXPLORE, InvokeFrom.DEBUGGER}
                        else CreatedByRole.END_USER
                    ),
                    created_by=user_id,
                )

                session.add(message_file)
                await session.commit()

                result.append((message_file.id, message.save_as))

        return result
