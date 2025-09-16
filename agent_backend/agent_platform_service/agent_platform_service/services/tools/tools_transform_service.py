import json
import logging
from typing import Optional, Union
from datetime import datetime

from nltk.sem.chat80 import continent

from agent_platform_common.configs import agent_platform_config
from agent_platform_core.models.db_model.tools import ApiToolProvider, BuiltinToolProvider, WorkflowToolProvider
from agent_platform_core.tools.entities.api_entities import UserTool, UserToolProvider
from agent_platform_core.tools.entities.common_entities import I18nObject
from agent_platform_core.tools.entities.tool_bundle import ApiToolBundle
from agent_platform_core.tools.entities.tool_entities import (
    ApiProviderAuthType,
    ToolParameter,
    ToolProviderCredentials,
    ToolProviderType,
)
from agent_platform_core.tools.plugin_tool.provider import PluginToolProviderController
from agent_platform_core.tools.plugin_tool.tool import PluginTool
from agent_platform_core.tools.provider.api_tool_provider import ApiToolProviderController
from agent_platform_core.tools.provider.builtin_tool_provider import BuiltinToolProviderController
from agent_platform_core.tools.provider.workflow_tool_provider import WorkflowToolProviderController
from agent_platform_core.tools.tool.tool import Tool
from agent_platform_core.tools.tool.workflow_tool import WorkflowTool
from agent_platform_core.tools.utils.configuration import ToolConfigurationManager

from agent_platform_core.tools.utils.configuration import ProviderConfigEncrypter
from yarl import URL

logger = logging.getLogger(__name__)


class ToolTransformService:
    @classmethod
    def get_plugin_icon_url(cls, tenant_id: str, filename: str) -> str:
        url_prefix = (
            URL(agent_platform_config.CONSOLE_API_URL or "/") / "console" / "api" / "workspaces" / "current" / "plugin" / "icon"
        )
        return str(url_prefix % {"tenant_id": tenant_id, "filename": filename})

    @staticmethod
    def get_tool_provider_icon_url(provider_type: str, provider_name: str, icon: str) -> Union[str, dict]:
        """
            get tool provider icon url
        """
        url_prefix = (agent_platform_config.CONSOLE_API_URL
                      + "/console/api/workspaces/current/tool-provider/")

        if provider_type == ToolProviderType.BUILT_IN.value:
            return url_prefix + 'builtin/' + provider_name + '/icon'
        elif provider_type in [ToolProviderType.API.value, ToolProviderType.WORKFLOW.value]:
            try:
                return json.loads(icon)
            except:
                return {
                    "background": "#252525",
                    "content": "\ud83d\ude01"
                }

        return ''

    @staticmethod
    def repack_provider(provider: Union[dict, UserToolProvider], tenant_id: str = None):
        """
            repack provider

            :param provider: the provider dict
        """
        if isinstance(provider, dict) and 'icon' in provider:
            provider['icon'] = ToolTransformService.get_tool_provider_icon_url(
                provider_type=provider['type'],
                provider_name=provider['name'],
                icon=provider['icon']
            )
        elif isinstance(provider, UserToolProvider):
            if provider.plugin_id:
                if isinstance(provider.icon, str):
                    provider.icon = ToolTransformService.get_plugin_icon_url(
                        tenant_id=tenant_id, filename=provider.icon
                    )
            else:
                provider.icon = ToolTransformService.get_tool_provider_icon_url(
                    provider_type=provider.type.value,
                    provider_name=provider.name,
                    icon=provider.icon
                )

    @staticmethod
    def builtin_provider_to_user_provider(
            provider_controller: BuiltinToolProviderController | PluginToolProviderController,
            db_provider: Optional[BuiltinToolProvider],
            decrypt_credentials: bool = True,
    ) -> UserToolProvider:
        """
        convert provider controller to user provider
        """
        if hasattr(provider_controller, 'tenant_id'):
            result = UserToolProvider(
                id=provider_controller.entity.identity.name,
                author=provider_controller.entity.identity.author,
                name=provider_controller.entity.identity.name,
                description=I18nObject(
                    en_US=provider_controller.entity.identity.description.en_US,
                    zh_Hans=provider_controller.entity.identity.description.zh_Hans,
                    pt_BR=provider_controller.entity.identity.description.pt_BR,
                ),
                icon=provider_controller.entity.identity.icon,
                label=I18nObject(
                    en_US=provider_controller.entity.identity.label.en_US,
                    zh_Hans=provider_controller.entity.identity.label.zh_Hans,
                    pt_BR=provider_controller.entity.identity.label.pt_BR,
                ),
                type=ToolProviderType.BUILT_IN,
                masked_credentials={},
                is_team_authorization=False,
                tools=[],
                labels=provider_controller.tool_labels
            )
        else:
            result = UserToolProvider(
                id=provider_controller.identity.name,
                author=provider_controller.identity.author,
                name=provider_controller.identity.name,
                description=I18nObject(
                    en_US=provider_controller.identity.description.en_US,
                    zh_Hans=provider_controller.identity.description.zh_Hans,
                    pt_BR=provider_controller.identity.description.pt_BR,
                ),
                icon=provider_controller.identity.icon,
                label=I18nObject(
                    en_US=provider_controller.identity.label.en_US,
                    zh_Hans=provider_controller.identity.label.zh_Hans,
                    pt_BR=provider_controller.identity.label.pt_BR,
                ),
                type=ToolProviderType.BUILT_IN,
                masked_credentials={},
                is_team_authorization=False,
                tools=[],
                labels=provider_controller.tool_labels
            )

        if isinstance(provider_controller, PluginToolProviderController):
            result.plugin_id = provider_controller.plugin_id
            result.plugin_unique_identifier = provider_controller.plugin_unique_identifier

            # add tools
            # result.tools



        # get credentials schema
        schema = {x.to_basic_provider_config().name: x for x in provider_controller.get_credentials_schema()}

        for name, value in schema.items():
            if result.masked_credentials:
                result.masked_credentials[name] = ""

        # check if the provider need credentials
        if not provider_controller.need_credentials:
            result.is_team_authorization = True
            result.allow_delete = False
        elif db_provider:
            result.is_team_authorization = True

            if decrypt_credentials:
                credentials = db_provider.credentials

                # init tool configuration
                tool_configuration = ProviderConfigEncrypter(
                    tenant_id=db_provider.tenant_id,
                    config=[x.to_basic_provider_config() for x in provider_controller.get_credentials_schema()],
                    provider_type=provider_controller.provider_type.value,
                    provider_identity=provider_controller.entity.identity.name,
                )
                # decrypt the credentials and mask the credentials
                decrypted_credentials = tool_configuration.decrypt(data=credentials)
                masked_credentials = tool_configuration.mask_tool_credentials(data=decrypted_credentials)

                result.masked_credentials = masked_credentials
                result.original_credentials = decrypted_credentials

        return result


    @staticmethod
    async def async_api_provider_to_controller(
            db_provider: ApiToolProvider,
    ) -> ApiToolProviderController:
        """
        convert provider controller to user provider
        """
        # package tool provider controller
        controller = await ApiToolProviderController.from_db_async(
            db_provider=db_provider,
            auth_type=ApiProviderAuthType.API_KEY if db_provider.credentials['auth_type'] == 'api_key' else
            ApiProviderAuthType.NONE
        )

        return controller

    @staticmethod
    def api_provider_to_controller(
            db_provider: ApiToolProvider,
    ) -> ApiToolProviderController:
        """
        convert provider controller to user provider
        """
        # package tool provider controller
        controller = ApiToolProviderController.from_db(
            db_provider=db_provider,
            auth_type=ApiProviderAuthType.API_KEY if db_provider.credentials['auth_type'] == 'api_key' else
            ApiProviderAuthType.NONE
        )

        return controller

    @staticmethod
    def workflow_provider_to_controller(
            db_provider: WorkflowToolProvider
    ) -> WorkflowToolProviderController:
        """
        convert provider controller to provider
        """
        return WorkflowToolProviderController.from_db(db_provider)

    @staticmethod
    def workflow_provider_to_user_provider(
            provider_controller: WorkflowToolProviderController,
            labels: list[str] = None
    ):
        """
        convert provider controller to user provider
        """
        create_time = provider_controller.created_time
        dt = datetime.strptime(create_time, '%Y-%m-%d %H:%M:%S')
        create_time = dt.strftime('%Y%m%d%H%M%S')
        provider_controller.identity.name = provider_controller.identity.name + '_' + create_time

        # 获取当前的多语言标签对象
        label = provider_controller.identity.label

        # 创建一个字典来存储更新后的值
        updated_values = {}
        updated_values_new = {}

        # 遍历所有支持的语言字段（假设 model_fields_set 包含语言代码如 'en_US', 'zh_Hans' 等）
        for lang_code in label.model_fields_set:
            # 使用 getattr 获取当前语言的值
            current_value = getattr(label, lang_code)
            # 更新值（确保 create_time 是字符串，如果不是请先转换）
            updated_values[lang_code] = f"{current_value}_{create_time}"

        # 使用新值创建新的 I18nObject 实例
        provider_controller.identity.label = type(label)(**updated_values)

        for tool in provider_controller.tools:
            # 方法1：假设label有model_dump()方法（Pydantic模型）
            label = tool.identity.label
            for lang_code_new in label.model_fields_set:
                # 使用 getattr 获取当前语言的值
                current_value = getattr(label, lang_code_new)
                # 更新值（确保 create_time 是字符串，如果不是请先转换）
                updated_values_new[lang_code_new] = f"{current_value}_{create_time}"
            tool.identity.label = type(label)(**updated_values)


        return UserToolProvider(
            id=provider_controller.provider_id,
            author=provider_controller.identity.author,
            name=provider_controller.identity.name,
            description=I18nObject(
                en_US=provider_controller.identity.description.en_US,
                zh_Hans=provider_controller.identity.description.zh_Hans,
            ),
            icon=provider_controller.identity.icon,
            label=I18nObject(
                en_US=provider_controller.identity.label.en_US,
                zh_Hans=provider_controller.identity.label.zh_Hans,
            ),
            type=ToolProviderType.WORKFLOW,
            masked_credentials={},
            is_team_authorization=True,
            tools=[],
            labels=labels or [],
            created_time=provider_controller.created_time
        )

    @staticmethod
    def api_provider_to_user_provider(
            provider_controller: ApiToolProviderController,
            db_provider: ApiToolProvider,
            decrypt_credentials: bool = True,
            labels: list[str] = None
    ) -> UserToolProvider:
        """
        convert provider controller to user provider
        """
        username = 'Anonymous'
        try:
            username = db_provider.user.name
        except Exception as e:
            logger.error(f'failed to get user name for api provider {db_provider.id}: {str(e)}')
        # add provider into providers
        credentials = db_provider.credentials
        result = UserToolProvider(
            id=db_provider.id,
            author=username,
            name=db_provider.name,
            description=I18nObject(
                en_US=db_provider.description,
                zh_Hans=db_provider.description,
            ),
            icon=db_provider.icon,
            label=I18nObject(
                en_US=db_provider.name,
                zh_Hans=db_provider.name,
            ),
            type=ToolProviderType.API,
            masked_credentials={},
            is_team_authorization=True,
            tools=[],
            labels=labels or [],
            created_time=db_provider.created_at.strftime("%Y-%m-%d %H:%M:%S")
        )

        if decrypt_credentials:
            # init tool configuration
            tool_configuration = ToolConfigurationManager(
                tenant_id=db_provider.tenant_id,
                provider_controller=provider_controller
            )

            # decrypt the credentials and mask the credentials
            decrypted_credentials = tool_configuration.decrypt_tool_credentials(credentials=credentials)
            masked_credentials = tool_configuration.mask_tool_credentials(credentials=decrypted_credentials)

            result.masked_credentials = masked_credentials

        return result

    @staticmethod
    def tool_to_user_tool(
            tool: Union[ApiToolBundle, WorkflowTool, Tool],
            credentials: dict = None,
            tenant_id: str = None,
            labels: list[str] = None
    ) -> UserTool:
        """
        convert tool to user tool
        """
        if isinstance(tool, Tool) or isinstance(tool, PluginTool):
            # fork tool runtime
            tool = tool.fork_tool_runtime(runtime={
                'credentials': credentials,
                'tenant_id': tenant_id,
            })

            # get tool parameters
            if hasattr(tool, 'entity'):
                parameters = tool.entity.parameters or []
            else:
                parameters = tool.parameters or []

            # get tool runtime parameters
            runtime_parameters = tool.get_runtime_parameters() or []
            # override parameters
            current_parameters = parameters.copy()
            for runtime_parameter in runtime_parameters:
                found = False
                for index, parameter in enumerate(current_parameters):
                    if parameter.name == runtime_parameter.name and parameter.form == runtime_parameter.form:
                        current_parameters[index] = runtime_parameter
                        found = True
                        break

                if not found and runtime_parameter.form == ToolParameter.ToolParameterForm.FORM:
                    current_parameters.append(runtime_parameter)

            # 区分builtin tool和plugin tool
            if hasattr(tool, 'entity'):
                return UserTool(
                    author=tool.entity.identity.author,
                    name=tool.entity.identity.name,
                    label=tool.entity.identity.label,
                    description=tool.entity.description.human if tool.entity.description else I18nObject(en_US=""),
                    parameters=current_parameters,
                    labels=labels
                )
            else:
                return UserTool(
                    author=tool.identity.author,
                    name=tool.identity.name,
                    label=tool.identity.label,
                    description=tool.description.human,
                    parameters=current_parameters,
                    labels=labels
                )

        if isinstance(tool, ApiToolBundle):
            return UserTool(
                author=tool.author,
                name=tool.operation_id,
                label=I18nObject(
                    en_US=tool.operation_id,
                    zh_Hans=tool.operation_id
                ),
                description=I18nObject(
                    en_US=tool.summary or '',
                    zh_Hans=tool.summary or ''
                ),
                parameters=tool.parameters,
                labels=labels,
            )
