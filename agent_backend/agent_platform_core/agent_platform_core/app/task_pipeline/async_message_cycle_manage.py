import asyncio
import logging
from asyncio import Task
from typing import Optional, Union

from sqlalchemy import select

from agent_platform_basic.models.db_model import Account
from agent_platform_common.configs import agent_platform_config
from agent_platform_core.app.entities.app_invoke_entities import (
    AdvancedChatAppGenerateEntity,
    AgentChatAppGenerateEntity,
    ChatAppGenerateEntity,
    CompletionAppGenerateEntity,
)
from agent_platform_core.app.entities.queue_entities import (
    QueueAnnotationReplyEvent,
    QueueMessageFileEvent,
    QueueRetrieverResourcesEvent,
)
from agent_platform_core.app.entities.task_entities import (
    EasyUITaskState,
    MessageFileStreamResponse,
    MessageReplaceStreamResponse,
    MessageStreamResponse,
    WorkflowTaskState,
)
from agent_platform_core.llm_generator.async_llm_generator import AsyncLLMGenerator
from agent_platform_core.tools.tool_file_manager import ToolFileManager
from agent_platform_basic.extensions.ext_database import async_db
from agent_platform_core.models.db_model.model import Conversation, MessageAnnotation, MessageFile, App
from agent_platform_core.models.enum_model.app_mode import AppMode


class AsyncMessageCycleManage:
    _application_generate_entity: Union[
        ChatAppGenerateEntity, CompletionAppGenerateEntity, AgentChatAppGenerateEntity, AdvancedChatAppGenerateEntity
    ]
    _task_state: Union[EasyUITaskState, WorkflowTaskState]

    async def _generate_conversation_name(self, conversation: Conversation, query: str) -> Optional[Task]:
        """
        Generate conversation name.
        :param conversation: conversation
        :param query: query
        :return: thread
        """
        if isinstance(self._application_generate_entity, CompletionAppGenerateEntity):
            return None

        is_first_message = self._application_generate_entity.conversation_id is None
        extras = self._application_generate_entity.extras
        auto_generate_conversation_name = extras.get("auto_generate_conversation_name", True)

        if auto_generate_conversation_name and is_first_message:
            # start generate thread
            producer = asyncio.create_task(self._generate_conversation_name_worker(conversation.id, query))

            return producer

        return None

    async def _generate_conversation_name_worker(self, conversation_id: str, query: str):
        async with async_db.AsyncSessionLocal() as session:
            result = await session.execute(
                select(Conversation).filter(Conversation.id == conversation_id)
            )

            conversation = result.scalar_one_or_none()

            if not conversation:
                return

            if conversation.mode != AppMode.COMPLETION.value:
                app_scalar = await session.execute(select(App).filter(App.id == conversation.app_id))
                app_model = app_scalar.scalar_one_or_none()
                if not app_model:
                    return

                # generate conversation name
                try:
                    name = await AsyncLLMGenerator.generate_conversation_name(app_model.tenant_id, query)
                    conversation.name = name
                except Exception as e:
                    if agent_platform_config.DEBUG:
                        logging.exception(f"generate conversation name failed, conversation_id: {conversation_id}")
                    pass

                await session.merge(conversation)
                await session.commit()

    async def _handle_annotation_reply(self, event: QueueAnnotationReplyEvent) -> Optional[MessageAnnotation]:
        """
        Handle annotation reply.
        :param event: event
        :return:
        """
        async with async_db.AsyncSessionLocal() as session:
            annotation_scalar = await session.execute(
                select(MessageAnnotation).filter(MessageAnnotation.id == event.message_annotation_id)
            )

            annotation = annotation_scalar.scalar_one_or_none()

            if annotation:
                account_scalar = await session.execute(select(Account).filter(Account.id == annotation.account_id))
                account = account_scalar.scalar_one_or_none()
                self._task_state.metadata["annotation_reply"] = {
                    "id": annotation.id,
                    "account": {"id": annotation.account_id, "name": account.name if account else "Agent Platform user"},
                }

                return annotation

        return None

    def _handle_retriever_resources(self, event: QueueRetrieverResourcesEvent) -> None:
        """
        Handle retriever resources.
        :param event: event
        :return:
        """
        if self._application_generate_entity.app_config.additional_features.show_retrieve_source:
            # self._task_state.metadata["retriever_resources"] = event.retriever_resources
            self._task_state.metadata.retriever_resources = event.retriever_resources

    async def _message_file_to_stream_response(self, event: QueueMessageFileEvent) -> Optional[MessageFileStreamResponse]:
        """
        Message file to stream response.
        :param event: event
        :return:
        """
        async with async_db.AsyncSessionLocal() as session:
            message_file_scalar = await session.execute(
                select(MessageFile).filter(MessageFile.id == event.message_file_id))
            message_file = message_file_scalar.scalar_one_or_none()

        if message_file:
            # get tool file id
            tool_file_id = message_file.url.split("/")[-1]
            # trim extension
            tool_file_id = tool_file_id.split(".")[0]

            # get extension
            if "." in message_file.url:
                extension = f'.{message_file.url.split(".")[-1]}'
                if len(extension) > 10:
                    extension = ".bin"
            else:
                extension = ".bin"
            # add sign url to local file
            if message_file.url.startswith("http"):
                url = message_file.url
            else:
                url = ToolFileManager.sign_file(tool_file_id=tool_file_id, extension=extension)

            return MessageFileStreamResponse(
                task_id=self._application_generate_entity.task_id,
                id=message_file.id,
                type=message_file.type,
                belongs_to=message_file.belongs_to or "user",
                url=url,
            )

        return None

    def _message_to_stream_response(
        self, answer: str, message_id: str, from_variable_selector: Optional[list[str]] = None
    ) -> MessageStreamResponse:
        """
        Message to stream response.
        :param answer: answer
        :param message_id: message id
        :return:
        """
        return MessageStreamResponse(
            task_id=self._application_generate_entity.task_id,
            id=message_id,
            answer=answer,
            from_variable_selector=from_variable_selector,
        )

    def _message_replace_to_stream_response(self, answer: str) -> MessageReplaceStreamResponse:
        """
        Message replace to stream response.
        :param answer: answer
        :return:
        """
        return MessageReplaceStreamResponse(task_id=self._application_generate_entity.task_id, answer=answer)
