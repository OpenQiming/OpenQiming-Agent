import logging
from collections.abc import Mapping
from typing import Any, cast

from sqlalchemy import select

from agent_platform_common.configs import agent_platform_config
from agent_platform_core.app.apps.advanced_chat.app_config_manager import AdvancedChatAppConfig
from agent_platform_core.app.apps.async_base_app_queue_manager import AsyncAppQueueManager
from agent_platform_core.app.apps.async_workflow_app_runner import AsyncWorkflowBasedAppRunner
from agent_platform_core.app.entities.app_invoke_entities import AdvancedChatAppGenerateEntity, InvokeFrom
from agent_platform_core.app.entities.queue_entities import (
    QueueAnnotationReplyEvent,
    QueueStopEvent,
    QueueTextChunkEvent,
)
from agent_platform_core.models.db_model.model import Conversation, App, EndUser, ConversationVariable, Message
from agent_platform_core.models.enum_model.enums import UserFrom
from agent_platform_core.models.enum_model.workflow import WorkflowType
from agent_platform_core.moderation.base import ModerationError
from agent_platform_core.workflow.callbacks import WorkflowCallback, WorkflowLoggingCallback
from agent_platform_core.workflow.entities.variable_pool import VariablePool
from agent_platform_core.workflow.enums import SystemVariableKey
from agent_platform_core.workflow.async_workflow_entry import WorkflowEntry
from agent_platform_basic.extensions.ext_database import async_db

logger = logging.getLogger(__name__)


class AdvancedChatAppRunner(AsyncWorkflowBasedAppRunner):
    """
    AdvancedChat Application Runner
    """

    def __init__(
        self,
        application_generate_entity: AdvancedChatAppGenerateEntity,
        queue_manager: AsyncAppQueueManager,
        conversation: Conversation,
        message: Message,
        dialogue_count: int,
    ) -> None:
        super().__init__(queue_manager)

        self.application_generate_entity = application_generate_entity
        self.conversation = conversation
        self.message = message
        self._dialogue_count = dialogue_count

    async def run(self) -> None:
        app_config = self.application_generate_entity.app_config
        app_config = cast(AdvancedChatAppConfig, app_config)

        user_id = None
        async with async_db.AsyncSessionLocal() as session:
            if self.application_generate_entity.invoke_from in {InvokeFrom.WEB_APP, InvokeFrom.SERVICE_API}:
                end_user = await session.execute(
                    select(EndUser).filter(EndUser.id == self.application_generate_entity.user_id))
                end_user = end_user.scalar_one_or_none()
                if end_user:
                    user_id = end_user.session_id
            else:
                user_id = self.application_generate_entity.user_id

            app_record = await session.execute(select(App).filter(App.id == app_config.app_id))
            app_record = app_record.scalar_one_or_none()

        if not app_record:
            raise ValueError("App not found")

        workflow = await self.get_workflow(app_model=app_record, workflow_id=app_config.workflow_id)
        if not workflow:
            raise ValueError("Workflow not initialized")

        workflow_callbacks: list[WorkflowCallback] = []
        if agent_platform_config.DEBUG:
            workflow_callbacks.append(WorkflowLoggingCallback())

        if self.application_generate_entity.single_iteration_run:
            # if only single iteration run is requested
            graph, variable_pool = await self._get_graph_and_variable_pool_of_single_iteration(
                workflow=workflow,
                node_id=self.application_generate_entity.single_iteration_run.node_id,
                user_inputs=dict(self.application_generate_entity.single_iteration_run.inputs),
            )
        elif self.application_generate_entity.single_loop_run:
            # if only single loop run is requested
            graph, variable_pool = await self._get_graph_and_variable_pool_of_single_loop(
                workflow=workflow,
                node_id=self.application_generate_entity.single_loop_run.node_id,
                user_inputs=dict(self.application_generate_entity.single_loop_run.inputs),
            )
        else:
            inputs = self.application_generate_entity.inputs
            query = self.application_generate_entity.query
            files = self.application_generate_entity.files

            # moderation
            if self.handle_input_moderation(
                app_record=app_record,
                app_generate_entity=self.application_generate_entity,
                inputs=inputs,
                query=query,
                message_id=self.message.id,
            ):
                return

            # annotation reply
            handle_annotation_reply_result = await self.handle_annotation_reply(
                app_record=app_record,
                message=self.message,
                query=query,
                app_generate_entity=self.application_generate_entity,
            )

            if handle_annotation_reply_result:
                return

            # Init conversation variables
            stmt = select(ConversationVariable).where(
                ConversationVariable.app_id == self.conversation.app_id,
                ConversationVariable.conversation_id == self.conversation.id,
            )
            async with async_db.AsyncSessionLocal() as session:
                result = await session.scalars(stmt)
                db_conversation_variables = result.all()
                if not db_conversation_variables:
                    # Create conversation variables if they don't exist.
                    db_conversation_variables = [
                        ConversationVariable.from_variable(
                            app_id=self.conversation.app_id, conversation_id=self.conversation.id, variable=variable
                        )
                        for variable in workflow.conversation_variables
                    ]
                    session.add_all(db_conversation_variables)
                    await session.commit()
                # Convert database entities to variables.
                conversation_variables = [item.to_variable() for item in db_conversation_variables]

            # Create a variable pool.
            system_inputs = {
                SystemVariableKey.QUERY: query,
                SystemVariableKey.FILES: files,
                SystemVariableKey.CONVERSATION_ID: self.conversation.id,
                SystemVariableKey.USER_ID: user_id,
                SystemVariableKey.DIALOGUE_COUNT: self._dialogue_count,
                SystemVariableKey.APP_ID: app_config.app_id,
                SystemVariableKey.WORKFLOW_ID: app_config.workflow_id,
                SystemVariableKey.WORKFLOW_RUN_ID: self.application_generate_entity.workflow_run_id,
            }

            # init variable pool
            variable_pool = VariablePool(
                system_variables=system_inputs,
                user_inputs=inputs,
                environment_variables=workflow.environment_variables,
                conversation_variables=conversation_variables,
            )

            # init graph
            graph = self._init_graph(graph_config=workflow.graph_dict)

        # RUN WORKFLOW
        workflow_entry = WorkflowEntry(
            tenant_id=workflow.tenant_id,
            app_id=workflow.app_id,
            workflow_id=workflow.id,
            workflow_type=WorkflowType.value_of(workflow.type),
            graph=graph,
            graph_config=workflow.graph_dict,
            user_id=self.application_generate_entity.user_id,
            user_from=(
                UserFrom.ACCOUNT
                if self.application_generate_entity.invoke_from in {InvokeFrom.EXPLORE, InvokeFrom.DEBUGGER}
                else UserFrom.END_USER
            ),
            invoke_from=self.application_generate_entity.invoke_from,
            call_depth=self.application_generate_entity.call_depth,
            variable_pool=variable_pool,
        )

        generator = workflow_entry.run(
            callbacks=workflow_callbacks,
        )
        async for event in generator:
            await self._handle_event(workflow_entry, event)

    def handle_input_moderation(
        self,
        app_record: App,
        app_generate_entity: AdvancedChatAppGenerateEntity,
        inputs: Mapping[str, Any],
        query: str,
        message_id: str,
    ) -> bool:
        try:
            # process sensitive_word_avoidance
            _, inputs, query = self.moderation_for_inputs(
                app_id=app_record.id,
                tenant_id=app_generate_entity.app_config.tenant_id,
                app_generate_entity=app_generate_entity,
                inputs=inputs,
                query=query,
                message_id=message_id,
            )
        except ModerationError as e:
            self._complete_with_stream_output(text=str(e), stopped_by=QueueStopEvent.StopBy.INPUT_MODERATION)
            return True

        return False

    async def handle_annotation_reply(
        self, app_record: App, message: Message, query: str, app_generate_entity: AdvancedChatAppGenerateEntity
    ) -> bool:
        annotation_reply = await self.query_app_annotations_to_reply(
            app_record=app_record,
            message=message,
            query=query,
            user_id=app_generate_entity.user_id,
            invoke_from=app_generate_entity.invoke_from,
        )

        if annotation_reply:
            await self._publish_event(QueueAnnotationReplyEvent(message_annotation_id=annotation_reply.id))

            self._complete_with_stream_output(
                text=annotation_reply.content, stopped_by=QueueStopEvent.StopBy.ANNOTATION_REPLY
            )
            return True

        return False

    def _complete_with_stream_output(self, text: str, stopped_by: QueueStopEvent.StopBy) -> None:
        """
        Direct output
        """
        self._publish_event(QueueTextChunkEvent(text=text))

        self._publish_event(QueueStopEvent(stopped_by=stopped_by))
