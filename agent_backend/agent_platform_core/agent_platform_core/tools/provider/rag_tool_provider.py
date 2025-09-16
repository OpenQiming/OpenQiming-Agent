from typing import Optional

from sqlalchemy import select

from agent_platform_basic.models.db_model import Account
from agent_platform_core.app.app_config.entities import VariableEntityType
from agent_platform_core.app.apps.workflow.app_config_manager import WorkflowAppConfigManager
from agent_platform_core.models.db_model.tools.rag_kb_table import RagKbTableProvider
from agent_platform_core.tools.entities.common_entities import I18nObject
from agent_platform_core.tools.entities.tool_entities import (
    ToolDescription,
    ToolIdentity,
    ToolParameter,
    ToolParameterOption,
    ToolProviderType,
)
from agent_platform_core.tools.provider.tool_provider import ToolProviderController
from agent_platform_core.tools.tool.rag_tool import RagTool
from agent_platform_core.tools.tool.tool import Tool
from agent_platform_core.tools.tool.workflow_tool import WorkflowTool
from agent_platform_core.tools.utils.workflow_configuration_sync import WorkflowToolConfigurationUtils
from agent_platform_basic.extensions.ext_database import db, async_db
from agent_platform_core.models.db_model.model import App
from agent_platform_core.models.enum_model.app_mode import AppMode
from agent_platform_core.models.db_model.tools import WorkflowToolProvider
from agent_platform_core.models.db_model.workflow import Workflow

VARIABLE_TO_PARAMETER_TYPE_MAPPING = {
    VariableEntityType.TEXT_INPUT: ToolParameter.ToolParameterType.STRING,
    VariableEntityType.PARAGRAPH: ToolParameter.ToolParameterType.STRING,
    VariableEntityType.SELECT: ToolParameter.ToolParameterType.SELECT,
    VariableEntityType.NUMBER: ToolParameter.ToolParameterType.NUMBER,
    VariableEntityType.FILE: ToolParameter.ToolParameterType.FILE,
    VariableEntityType.FILE_LIST: ToolParameter.ToolParameterType.FILES,
}


class RagProviderController(ToolProviderController):
    provider_id: str

    @classmethod
    def from_db(cls, db_provider: RagKbTableProvider) -> "RagProviderController":
        app = db_provider.app

        if not app:
            raise ValueError("app not found")

        controller = RagProviderController.model_validate(
            {
                "identity": {
                    "author": db_provider.user.name if db_provider.user_id and db_provider.user else "",
                    "name": db_provider.label,
                    "label": {"en_US": db_provider.label, "zh_Hans": db_provider.label},
                    "description": {"en_US": db_provider.description, "zh_Hans": db_provider.description},
                    "icon": db_provider.icon,
                },
                "credentials_schema": {},
                "provider_id": db_provider.id or "",

            }
        )

        # init tools

        controller.tools = [controller._get_db_provider_tool(db_provider)]

        return controller

    @classmethod
    async def async_from_db(cls, db_provider: RagKbTableProvider, query: str = "") -> "RagProviderController":

        controller = RagProviderController.model_validate(
            {
                "identity": {
                    "author": db_provider.creator,
                    "name": db_provider.kb_name,
                    "label": {"en_US": db_provider.kb_desc, "zh_Hans": db_provider.kb_desc},
                    "description": {"en_US": db_provider.kb_desc, "zh_Hans": db_provider.kb_desc},
                    "icon": db_provider.kb_icon,
                },
                "credentials_schema": {},
                "provider_id": db_provider.kb_id or "",
            }
        )
        # init tools

        controller.tools = [await controller._async_get_db_provider_tool(db_provider, query)]

        return controller

    def _get_db_provider_tool(self, db_provider: RagKbTableProvider, query: str = "") -> RagTool:
        params = []
        params.append(
            ToolParameter(
                name=query,
                label=I18nObject(en_US=query, zh_Hans=query),
                human_description=I18nObject(en_US=db_provider.kb_desc, zh_Hans=db_provider.kb_desc),
                placeholder=I18nObject(en_US=db_provider.kb_desc, zh_Hans=db_provider.kb_desc),
                type=VARIABLE_TO_PARAMETER_TYPE_MAPPING[VariableEntityType.TEXT_INPUT],
                form=ToolParameter.ToolParameterForm.FORM,
                llm_description=db_provider.kb_desc,
                required=True,
                options=[ToolParameterOption(
                    value=query,
                    label=I18nObject(en_US=db_provider.kb_desc, zh_Hans=db_provider.kb_desc)
                )],
            )
        )
        return RagTool(
            identity=ToolIdentity(
                author=db_provider.creator,
                name=db_provider.kb_name,
                label=I18nObject(en_US=db_provider.kb_desc, zh_Hans=db_provider.kb_desc),
                provider=self.provider_id,
                icon=db_provider.kb_icon,
            ),
            description=ToolDescription(
                human=I18nObject(en_US=db_provider.kb_desc, zh_Hans=db_provider.kb_desc),
                llm=db_provider.kb_desc,
            ),
            parameters=params,
            is_team_authorization=True,
            query=query,
            kb_id=db_provider.kb_id,
        )

    async def _async_get_db_provider_tool(self, db_provider: RagKbTableProvider, query: str = "") -> RagTool:

        params = []
        params.append(
            ToolParameter(
                name=db_provider.kb_name,
                label=I18nObject(en_US=query, zh_Hans=query),
                human_description=I18nObject(en_US=db_provider.kb_desc, zh_Hans=db_provider.kb_desc),
                placeholder=I18nObject(en_US=db_provider.kb_desc, zh_Hans=db_provider.kb_desc),
                type=VARIABLE_TO_PARAMETER_TYPE_MAPPING[VariableEntityType.TEXT_INPUT],
                form=ToolParameter.ToolParameterForm.FORM,
                llm_description=db_provider.kb_desc,
                required=True,
                options=[ToolParameterOption(
                    value=query,
                    label=I18nObject(en_US=db_provider.kb_desc, zh_Hans=db_provider.kb_desc)
                )],
            )
        )
        return RagTool(
            identity=ToolIdentity(
                author=db_provider.creator,
                name=db_provider.kb_name,
                label=I18nObject(en_US=db_provider.kb_desc, zh_Hans=db_provider.kb_desc),
                provider=self.provider_id,
                icon=db_provider.kb_icon,
            ),
            description=ToolDescription(
                human=I18nObject(en_US=db_provider.kb_desc, zh_Hans=db_provider.kb_desc),
                llm=db_provider.kb_desc,
            ),
            parameters=params,
            is_team_authorization=True,
            query=query,
            kb_id=db_provider.kb_id,
        )

    def get_tools(self, user_id: str, tenant_id: str) -> list[RagTool]:
        """
        fetch tools from database

        :param user_id: the user id
        :param tenant_id: the tenant id
        :return: the tools
        """
        if self.tools is not None:
            return self.tools

        db_providers: RagKbTableProvider = (
            db.session.query(RagKbTableProvider)
            .filter(
                RagKbTableProvider.tenant_id == tenant_id,
                RagKbTableProvider.kb_id == self.provider_id,
            )
            .first()
        )

        if not db_providers:
            return []

        self.tools = [self._get_db_provider_tool(db_providers)]

        return self.tools

    def get_tool(self, tool_name: str) -> Optional[RagTool]:
        """
        get tool by name

        :param tool_name: the name of the tool
        :return: the tool
        """
        if self.tools is None:
            return None

        for tool in self.tools:
            if tool.identity.name == tool_name:
                return tool

        return None