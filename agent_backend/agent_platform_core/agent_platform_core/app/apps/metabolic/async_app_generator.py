import asyncio
import contextvars
import logging
import uuid
from collections.abc import Generator, Mapping, Sequence
from typing import Any, Optional, Union, AsyncGenerator

from pydantic import ValidationError

from agent_platform_core import contexts
from agent_platform_common.configs import agent_platform_config
from agent_platform_core.app.app_config.features.file_upload.manager import FileUploadConfigManager
from agent_platform_core.app.apps.async_base_app_generator import AsyncBaseAppGenerator
from agent_platform_core.app.apps.async_base_app_queue_manager import AsyncAppQueueManager, GenerateTaskStoppedError, PublishFrom
from agent_platform_core.app.apps.metabolic.app_config_manager import MetabolicAppConfigManager
from agent_platform_core.app.apps.metabolic.async_app_queue_manager import AsyncMetabolicAppQueueManager
from agent_platform_core.app.apps.metabolic.async_app_runner import AsyncMetabolicAppRunner
from agent_platform_core.app.apps.metabolic.async_generate_response_converter import AsyncMetabolicAppGenerateResponseConverter
from agent_platform_core.app.apps.metabolic.async_generate_task_pipeline import AsyncMetabolicAppGenerateTaskPipeline
from agent_platform_core.app.entities.app_invoke_entities import InvokeFrom, WorkflowAppGenerateEntity
from agent_platform_core.app.entities.task_entities import WorkflowAppBlockingResponse, WorkflowAppStreamResponse
from agent_platform_core.model_runtime.errors.invoke import InvokeAuthorizationError, InvokeError
from agent_platform_core.ops.ops_trace_manager import TraceQueueManager
from agent_platform_core.factories import file_factory
from agent_platform_basic.models.db_model import Account
from agent_platform_core.models.db_model.model import App, EndUser
from agent_platform_core.models.db_model.workflow import Workflow

logger = logging.getLogger(__name__)


class AsyncMetabolicAppGenerator(AsyncBaseAppGenerator):
    async def generate(
        self,
        *,
        app_model: App,
        workflow: Workflow,
        user: Account | EndUser,
        args: Mapping[str, Any],
        invoke_from: InvokeFrom,
        streaming: bool = True,
        call_depth: int = 0,
        workflow_semaphore_id: Optional[str] = None,
    ) -> Mapping[str, Any] | AsyncGenerator[str, None]:
        files: Sequence[Mapping[str, Any]] = args.get("files") or []

        # parse files
        file_extra_config = FileUploadConfigManager.convert(workflow.features_dict, is_vision=False)
        system_files = await file_factory.async_build_from_mappings(
            mappings=files,
            tenant_id=app_model.tenant_id,
            config=file_extra_config,
        )

        # convert to app config
        app_config = MetabolicAppConfigManager.get_app_config(
            app_model=app_model,
            workflow=workflow,
        )

        # get tracing instance
        # trace_manager = TraceQueueManager(
        #     app_id=app_model.id,
        #     user_id=user.id if isinstance(user, Account) else user.session_id,
        # )

        inputs: Mapping[str, Any] = args["inputs"]
        workflow_run_id = str(uuid.uuid4())
        # init application generate entity
        application_generate_entity = WorkflowAppGenerateEntity(
            task_id=str(uuid.uuid4()),
            app_config=app_config,
            file_upload_config=file_extra_config,
            inputs=await self._prepare_user_inputs(
                user_inputs=inputs, variables=app_config.variables, tenant_id=app_model.tenant_id
            ),
            files=system_files,
            user_id=user.id,
            stream=streaming,
            invoke_from=invoke_from,
            call_depth=call_depth,
            # trace_manager=trace_manager,
            workflow_run_id=workflow_run_id,
        )
        contexts.tenant_id.set(application_generate_entity.app_config.tenant_id)

        return await self._generate(
            app_model=app_model,
            workflow=workflow,
            user=user,
            application_generate_entity=application_generate_entity,
            invoke_from=invoke_from,
            streaming=streaming,
            workflow_semaphore_id=workflow_semaphore_id,
        )

    async def _generate(
        self,
        *,
        app_model: App,
        workflow: Workflow,
        user: Union[Account, EndUser],
        application_generate_entity: WorkflowAppGenerateEntity,
        invoke_from: InvokeFrom,
        streaming: bool = True,
        workflow_semaphore_id: Optional[str] = None,
    ) -> Mapping[str, Any] | Generator[str, None, None]:
        # init queue manager
        queue_manager = AsyncMetabolicAppQueueManager(
            task_id=application_generate_entity.task_id,
            user_id=application_generate_entity.user_id,
            invoke_from=application_generate_entity.invoke_from,
            app_mode=app_model.mode,
        )

        producer = asyncio.create_task(self._generate_worker(application_generate_entity, queue_manager, contextvars.copy_context(), workflow_semaphore_id))

        # return response or stream generator
        response = await self._handle_response(
            application_generate_entity=application_generate_entity,
            workflow=workflow,
            queue_manager=queue_manager,
            user=user,
            stream=streaming,
        )

        return await AsyncMetabolicAppGenerateResponseConverter.convert(response=response, invoke_from=invoke_from)

    async def single_iteration_generate(
        self,
        app_model: App,
        workflow: Workflow,
        node_id: str,
        user: Account,
        args: Mapping[str, Any],
        streaming: bool = True,
    ) -> Mapping[str, Any] | AsyncGenerator[str, None]:
        """
        Generate App response.

        :param app_model: App
        :param workflow: Workflow
        :param user: account or end user
        :param args: request args
        :param invoke_from: invoke from source
        :param stream: is stream
        """
        if not node_id:
            raise ValueError("node_id is required")

        if args.get("inputs") is None:
            raise ValueError("inputs is required")

        # convert to app config
        app_config = MetabolicAppConfigManager.get_app_config(app_model=app_model, workflow=workflow)

        # init application generate entity
        application_generate_entity = WorkflowAppGenerateEntity(
            task_id=str(uuid.uuid4()),
            app_config=app_config,
            inputs={},
            files=[],
            user_id=user.id,
            stream=streaming,
            invoke_from=InvokeFrom.DEBUGGER,
            extras={"auto_generate_conversation_name": False},
            single_iteration_run=WorkflowAppGenerateEntity.SingleIterationRunEntity(
                node_id=node_id, inputs=args["inputs"]
            ),
        )
        contexts.tenant_id.set(application_generate_entity.app_config.tenant_id)

        return await self._generate(
            app_model=app_model,
            workflow=workflow,
            user=user,
            invoke_from=InvokeFrom.DEBUGGER,
            application_generate_entity=application_generate_entity,
            streaming=streaming,
        )

    async def _generate_worker(
        self,
        application_generate_entity: WorkflowAppGenerateEntity,
        queue_manager: AsyncAppQueueManager,
        context: contextvars.Context,
        workflow_semaphore_id: Optional[str] = None,
    ) -> None:
        """
        Generate worker.
        :param application_generate_entity: application generate entity
        :param queue_manager: queue manager
        :param workflow_semaphore_id: workflow semaphore id
        :return:
        """
        for var, val in context.items():
            var.set(val)
        try:
            # workflow app
            runner = AsyncMetabolicAppRunner(
                application_generate_entity=application_generate_entity,
                queue_manager=queue_manager,
                workflow_semaphore_id=workflow_semaphore_id,
            )

            await runner.run()
        except GenerateTaskStoppedError:
            pass
        except InvokeAuthorizationError:
            await queue_manager.publish_error(
                InvokeAuthorizationError("Incorrect API key provided"), PublishFrom.APPLICATION_MANAGER
            )
        except ValidationError as e:
            logger.exception("Validation Error when generating")
            await queue_manager.publish_error(e, PublishFrom.APPLICATION_MANAGER)
        except (ValueError, InvokeError) as e:
            if agent_platform_config.DEBUG:
                logger.exception("Error when generating")
            await queue_manager.publish_error(e, PublishFrom.APPLICATION_MANAGER)
        except Exception as e:
            logger.exception("Unknown Error when generating")
            await queue_manager.publish_error(e, PublishFrom.APPLICATION_MANAGER)
        finally:
            pass

    async def _handle_response(
        self,
        application_generate_entity: WorkflowAppGenerateEntity,
        workflow: Workflow,
        queue_manager: AsyncAppQueueManager,
        user: Union[Account, EndUser],
        stream: bool = False,
    ) -> Union[WorkflowAppBlockingResponse, AsyncGenerator[WorkflowAppStreamResponse, None]]:
        """
        Handle response.
        :param application_generate_entity: application generate entity
        :param workflow: workflow
        :param queue_manager: queue manager
        :param user: account or end user
        :param stream: is stream
        :return:
        """
        # init generate task pipeline
        generate_task_pipeline = AsyncMetabolicAppGenerateTaskPipeline(
            application_generate_entity=application_generate_entity,
            workflow=workflow,
            queue_manager=queue_manager,
            user=user,
            stream=stream,
        )

        try:
            return await generate_task_pipeline.process()
        except ValueError as e:
            if e.args[0] == "I/O operation on closed file.":  # ignore this error
                raise GenerateTaskStoppedError()
            else:
                logger.exception(
                    f"Fails to process generate task pipeline, task_id: {application_generate_entity.task_id}"
                )
                raise e
