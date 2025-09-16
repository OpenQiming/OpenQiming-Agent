import json
import logging
from copy import deepcopy
from typing import Any, Optional, Union

from sqlalchemy import select

from agent_platform_basic.libs.redis_utils import RedisUtils
from agent_platform_core.file import FILE_MODEL_IDENTITY, File, FileTransferMethod
from agent_platform_core.tools.entities.tool_entities import ToolInvokeMessage, ToolParameter, ToolProviderType
from agent_platform_core.tools.tool.tool import Tool
from agent_platform_basic.extensions.ext_database import db, async_db
from agent_platform_basic.models.db_model import Account
from agent_platform_core.models.db_model.model import App, EndUser
from agent_platform_core.models.db_model.workflow import Workflow

logger = logging.getLogger(__name__)


class WorkflowTool(Tool):
    workflow_app_id: str
    workflow_id: str
    version: str
    workflow_entities: dict[str, Any]
    workflow_call_depth: int
    semaphore_id: Optional[str] = None

    label: str

    """
    Workflow tool.
    """

    def tool_provider_type(self) -> ToolProviderType:
        """
        get the tool provider type

        :return: the tool provider type
        """
        return ToolProviderType.WORKFLOW

    def _invoke(
        self, user_id: str, tool_parameters: dict[str, Any]
    ) -> Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        """
        invoke the tool
        """
        app = self._get_app(app_id=self.workflow_app_id)
        logging.debug(f'version=self.version:{self.version}')
        workflow = self._get_workflow(app_id=self.workflow_app_id, version=self.version)

        # transform the tool parameters
        tool_parameters, files = self._transform_args(tool_parameters=tool_parameters)

        from agent_platform_core.app.apps.workflow.app_generator import WorkflowAppGenerator

        generator = WorkflowAppGenerator()
        assert self.runtime is not None
        assert self.runtime.invoke_from is not None
        result = generator.generate(
            app_model=app,
            workflow=workflow,
            user=self._get_user(user_id),
            args={"inputs": tool_parameters, "files": files},
            invoke_from=self.runtime.invoke_from,
            streaming=False,
            call_depth=self.workflow_call_depth + 1,
            workflow_thread_pool_id=self.semaphore_id,
        )
        assert isinstance(result, dict)
        data = result.get("data", {})

        if data.get("error"):
            raise Exception(data.get("error"))

        result = []

        outputs = data.get("outputs")
        if outputs == None:
            outputs = {}
        else:
            outputs, files = self._extract_files(outputs)
            for file in files:
                result.append(self.create_file_message(file))

        result.append(self.create_text_message(json.dumps(outputs, ensure_ascii=False)))
        result.append(self.create_json_message(outputs))

        return result

    async def _async_invoke(
        self, user_id: str, tool_parameters: dict[str, Any]
    ) -> Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        """
        invoke the tool
        """
        app = await self._async_get_app(app_id=self.workflow_app_id)
        logging.debug(f'version=self.version:{self.version}')
        workflow = await self._async_get_workflow(workflow_id=self.workflow_id)

        # transform the tool parameters
        tool_parameters, files = self._transform_args(tool_parameters=tool_parameters)

        from agent_platform_core.app.apps.workflow.async_app_generator import AsyncWorkflowAppGenerator

        generator = AsyncWorkflowAppGenerator()
        assert self.runtime is not None
        assert self.runtime.invoke_from is not None
        result = await generator.generate(
            app_model=app,
            workflow=workflow,
            user=await self._async_get_user(user_id),
            args={"inputs": tool_parameters, "files": files},
            invoke_from=self.runtime.invoke_from,
            streaming=False,
            call_depth=self.workflow_call_depth + 1,
            workflow_semaphore_id=self.semaphore_id,
        )
        assert isinstance(result, dict)
        data = result.get("data", {})

        if data.get("error"):
            raise Exception(data.get("error"))

        result = []

        outputs = data.get("outputs")
        if outputs == None:
            outputs = {}
        else:
            outputs, files = self._extract_files(outputs)
            for file in files:
                result.append(self.create_file_message(file))

        result.append(self.create_text_message(json.dumps(outputs, ensure_ascii=False)))
        result.append(self.create_json_message(outputs))

        return result

    def _get_user(self, user_id: str) -> Union[EndUser, Account]:
        """
        get the user by user id
        """

        user = db.session.query(EndUser).filter(EndUser.id == user_id).first()
        if not user:
            user = db.session.query(Account).filter(Account.id == user_id).first()

        if not user:
            raise ValueError("user not found")

        return user

    async def _async_get_user(self, user_id: str) -> Union[EndUser, Account]:
        """
            get the user by user id
        """
        async with async_db.AsyncSessionLocal() as session:
            user = await session.execute(select(EndUser).filter(EndUser.id == user_id))
            user = user.scalar_one_or_none()
            if not user:
                user = await session.execute(select(Account).filter(Account.id == user_id))
                user = user.scalar_one_or_none()
        if not user:
            raise ValueError("user not found")

        return user

    def fork_tool_runtime(self, runtime: dict[str, Any]) -> 'WorkflowTool':
        """
        fork a new tool with meta data

        :param meta: the meta data of a tool call processing, tenant_id is required
        :return: the new tool
        """
        return self.__class__(
            identity=deepcopy(self.identity),
            parameters=deepcopy(self.parameters),
            description=deepcopy(self.description),
            runtime=Tool.Runtime(**runtime),
            workflow_app_id=self.workflow_app_id,
            workflow_id=self.workflow_id,
            workflow_entities=self.workflow_entities,
            workflow_call_depth=self.workflow_call_depth,
            version=self.version,
            label=self.label,
        )

    def _get_workflow(self, app_id: str, version: str) -> Workflow:
        """
        get the workflow by app id and version
        """
        if not version:
            workflow = (
                db.session.query(Workflow)
                .filter(Workflow.app_id == app_id, Workflow.version != "draft")
                .order_by(Workflow.created_at.desc())
                .first()
            )
        else:
            workflow = db.session.query(Workflow).filter(Workflow.app_id == app_id, Workflow.version == version).first()

        if not workflow:
            raise ValueError("workflow not found or not published")

        return workflow

    @RedisUtils.cacheable_with_mutex("agent_platform_workflow_by_workflow_id: ",
                                     "agent_platform_get_workflow_with_mutex_by_workflow_id: ",
                                     ["workflow_id"],
                                     60)
    async def _async_get_workflow(self, workflow_id: str) -> Workflow:
        """
            get the workflow by app id and version
        """
        async with async_db.AsyncSessionLocal() as session:
                workflow = await session.execute(select(Workflow).filter(
                    Workflow.id == workflow_id
                ))
                workflow = workflow.scalar_one_or_none()

        if not workflow:
            raise ValueError("workflow not found or not published")

        return workflow

    def _get_app(self, app_id: str) -> App:
        """
        get the app by app id
        """
        app = db.session.query(App).filter(App.id == app_id).first()
        if not app:
            raise ValueError("app not found")

        return app

    @RedisUtils.cacheable_with_mutex("agent_platform_app_by_app_id: ",
                                     "agent_platform_get_app_with_mutex_by_app_id: ",
                                     ["app_id"],
                                     60)
    async def _async_get_app(self, app_id: str) -> App:
        """
            get the app by app id
        """
        async with async_db.AsyncSessionLocal() as session:
            app = await session.execute(select(App).filter(App.id == app_id))
            app = app.scalar_one_or_none()
        if not app:
            raise ValueError("app not found")

        return app

    def _transform_args(self, tool_parameters: dict) -> tuple[dict, list[dict]]:
        """
        transform the tool parameters

        :param tool_parameters: the tool parameters
        :return: tool_parameters, files
        """
        parameter_rules = self.get_all_runtime_parameters()
        parameters_result = {}
        files = []
        for parameter in parameter_rules:
            if parameter.type == ToolParameter.ToolParameterType.SYSTEM_FILES:
                file = tool_parameters.get(parameter.name)
                if file:
                    try:
                        file_var_list = [File.model_validate(f) for f in file]
                        for file in file_var_list:
                            file_dict: dict[str, str | None] = {
                                "transfer_method": file.transfer_method.value,
                                "type": file.type.value,
                            }
                            if file.transfer_method == FileTransferMethod.TOOL_FILE:
                                file_dict["tool_file_id"] = file.related_id
                            elif file.transfer_method == FileTransferMethod.LOCAL_FILE:
                                file_dict["upload_file_id"] = file.related_id
                            elif file.transfer_method == FileTransferMethod.REMOTE_URL:
                                file_dict["url"] = file.generate_url()

                            files.append(file_dict)
                    except Exception as e:
                        logger.exception(f"Failed to transform file {file}")
            else:
                parameters_result[parameter.name] = tool_parameters.get(parameter.name)

        return parameters_result, files

    def _extract_files(self, outputs: dict) -> tuple[dict, list[File]]:
        """
        extract files from the result

        :param result: the result
        :return: the result, files
        """
        files = []
        result = {}
        for key, value in outputs.items():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and item.get("agent_platform_model_identity") == FILE_MODEL_IDENTITY:
                        file = File.model_validate(item)
                        files.append(file)
            elif isinstance(value, dict) and value.get("agent_platform_model_identity") == FILE_MODEL_IDENTITY:
                file = File.model_validate(value)
                files.append(file)

            result[key] = value
        return result, files
