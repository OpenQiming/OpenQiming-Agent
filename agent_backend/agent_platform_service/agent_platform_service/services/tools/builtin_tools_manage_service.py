import json
import logging

from sqlalchemy import text

from agent_platform_basic.extensions.ext_database import db
from agent_platform_common.configs import agent_platform_config
from agent_platform_core.model_runtime.utils.encoders import jsonable_encoder
from agent_platform_core.models.db_model.tools import BuiltinToolProvider
from agent_platform_core.tools.entities.api_entities import UserTool, UserToolProvider
from agent_platform_core.tools.errors import (
    ToolNotFoundError,
    ToolProviderCredentialValidationError,
    ToolProviderNotFoundError
)
from agent_platform_core.tools.plugin_tool.provider import PluginToolProviderController
from agent_platform_core.tools.plugin_tool.tool import PluginTool
from agent_platform_core.tools.provider.builtin._positions import BuiltinToolProviderSort
from agent_platform_core.tools.provider.tool_provider import ToolProviderController
from agent_platform_core.tools.tool_label_manager import ToolLabelManager
from agent_platform_core.tools.tool_manager import ToolManager
from agent_platform_core.tools.utils.configuration import ToolConfigurationManager, ProviderConfigEncrypter
from agent_platform_service.services.tools.tools_transform_service import ToolTransformService
from agent_platform_core.plugin.entities.plugin import ToolProviderID


logger = logging.getLogger(__name__)


class BuiltinToolManageService:
    @staticmethod
    def list_builtin_tool_provider_tools(
            user_id: str, tenant_id: str, provider: str
    ) -> list[UserTool]:
        """
            list builtin tool provider tools
        """
        provider_controller: ToolProviderController = ToolManager.get_builtin_provider(provider, tenant_id)
        tools = provider_controller.get_tools()

        tool_provider_configurations = ToolConfigurationManager(tenant_id=tenant_id,
                                                                provider_controller=provider_controller)
        # check if user has added the provider
        builtin_provider: BuiltinToolProvider = db.session.query(BuiltinToolProvider).filter(
            BuiltinToolProvider.tenant_id == tenant_id,
            BuiltinToolProvider.provider == provider,
        ).first()

        credentials = {}
        if builtin_provider is not None:
            # get credentials
            credentials = builtin_provider.credentials
            credentials = tool_provider_configurations.decrypt_tool_credentials(credentials)

        result = []
        for tool in tools:
            result.append(ToolTransformService.tool_to_user_tool(
                tool=tool,
                credentials=credentials,
                tenant_id=tenant_id,
                labels=ToolLabelManager.get_tool_labels(provider_controller)
            ))

        return result

    @staticmethod
    def list_builtin_provider_credentials_schema(provider_name: str, tenant_id: str):
        """
        list builtin provider credentials schema

        :param provider_name: the name of the provider
        :param tenant_id: the id of the tenant
        :return: the list of tool providers
        """
        provider = ToolManager.get_builtin_provider(provider_name, tenant_id)
        return jsonable_encoder(provider.get_credentials_schema())

    @staticmethod
    def update_builtin_tool_provider(
            user_id: str, tenant_id: str, provider_name: str, credentials: dict
    ):
        """
            update builtin tool provider
        """
        # get if the provider exists
        provider: BuiltinToolProvider = db.session.query(BuiltinToolProvider).filter(
            BuiltinToolProvider.tenant_id == tenant_id,
            BuiltinToolProvider.provider == provider_name,
        ).first()

        try:
            # get provider
            provider_controller = ToolManager.get_builtin_provider(provider_name, tenant_id)
            if not provider_controller.need_credentials:
                raise ValueError(f'provider {provider_name} does not need credentials')

            # if isinstance(provider, BuiltinToolProvider):
            if isinstance(provider_controller, PluginToolProviderController):
                tool_configuration = ProviderConfigEncrypter(
                    tenant_id=tenant_id,
                    config=[x.to_basic_provider_config() for x in provider_controller.get_credentials_schema()],
                    provider_type=provider_controller.provider_type.value,
                    provider_identity=provider_controller.entity.identity.name,
                )
            else:
                tool_configuration = ToolConfigurationManager(tenant_id=tenant_id,
                                                              provider_controller=provider_controller)
                # get original credentials if exists
                if provider is not None:
                    original_credentials = tool_configuration.decrypt_tool_credentials(provider.credentials)
                    masked_credentials = tool_configuration.mask_tool_credentials(original_credentials)
                    # check if the credential has changed, save the original credential
                    for name, value in credentials.items():
                        if name in masked_credentials and value == masked_credentials[name]:
                            credentials[name] = original_credentials[name]

            # validate credentials
            if isinstance(provider_controller, PluginToolProviderController):
                provider_controller.validate_credentials(user_id, credentials)
                # encrypt credentials
                credentials = tool_configuration.encrypt(credentials)
            else:
                provider_controller.validate_credentials(credentials)
                # encrypt credentials
                credentials = tool_configuration.encrypt_tool_credentials(credentials)

        except (ToolProviderNotFoundError, ToolNotFoundError, ToolProviderCredentialValidationError) as e:
            raise ValueError(str(e))

        if provider is None:
            # create provider
            provider = BuiltinToolProvider(
                tenant_id=tenant_id,
                user_id=user_id,
                provider=provider_name,
                encrypted_credentials=json.dumps(credentials, ensure_ascii=False),
            )

            db.session.add(provider)
            db.session.commit()

        else:
            provider.encrypted_credentials = json.dumps(credentials, ensure_ascii=False)
            db.session.add(provider)
            db.session.commit()

            # delete cache
            tool_configuration.delete_tool_credentials_cache()

        return {'result': 'success'}

    @staticmethod
    def get_builtin_tool_provider_credentials(
            user_id: str, tenant_id: str, provider: str
    ):
        """
            get builtin tool provider credentials
        """
        provider: BuiltinToolProvider = db.session.query(BuiltinToolProvider).filter(
            BuiltinToolProvider.tenant_id == tenant_id,
            BuiltinToolProvider.provider == provider,
        ).first()

        if provider is None:
            return {}

        provider_controller = ToolManager.get_builtin_provider(provider.provider)
        tool_configuration = ToolConfigurationManager(tenant_id=tenant_id, provider_controller=provider_controller)
        credentials = tool_configuration.decrypt_tool_credentials(provider.credentials)
        credentials = tool_configuration.mask_tool_credentials(credentials)
        return credentials

    @staticmethod
    def delete_builtin_tool_provider(
            user_id: str, tenant_id: str, provider_name: str
    ):
        """
            delete tool provider
        """
        provider: BuiltinToolProvider = db.session.query(BuiltinToolProvider).filter(
            BuiltinToolProvider.tenant_id == tenant_id,
            BuiltinToolProvider.provider == provider_name,
        ).first()

        if provider is None:
            raise ValueError(f'you have not added provider {provider_name}')

        db.session.delete(provider)
        db.session.commit()

        # delete cache
        provider_controller = ToolManager.get_builtin_provider(provider_name)
        tool_configuration = ToolConfigurationManager(tenant_id=tenant_id, provider_controller=provider_controller)
        tool_configuration.delete_tool_credentials_cache()

        return {'result': 'success'}

    @staticmethod
    def get_builtin_tool_provider_icon(
            provider: str
    ):
        """
            get tool provider icon and it's mimetype
        """
        icon_path, mime_type = ToolManager.get_hardcoded_provider_icon(provider)
        with open(icon_path, 'rb') as f:
            icon_bytes = f.read()

        return icon_bytes, mime_type

    @staticmethod
    def list_builtin_tools(
            user_id: str, tenant_id: str
    ) -> list[UserToolProvider]:
        """
            list builtin tools
        """
        # get all builtin providers
        provider_controllers = ToolManager.list_builtin_providers(tenant_id)

        # get all user added providers
        db_providers: list[BuiltinToolProvider] = db.session.query(BuiltinToolProvider).filter(
            BuiltinToolProvider.tenant_id.in_([tenant_id, agent_platform_config.GLOBAL_TENANT_ID])
        ).all() or []

        # rewrite db_providers
        for db_provider in db_providers:
            db_provider.provider = str(ToolProviderID(db_provider.provider))

        # find provider
        find_provider = lambda provider: next(
            filter(lambda db_provider: db_provider.provider == provider, db_providers), None)


        #是否订阅
        sql = '''
            select plugin_id from subscription where account_id=:account_id
        '''
        result = db.session.execute(text(sql), {"account_id":user_id})
        rows = result.mappings().all()
        plugin_id_sub = [r['plugin_id'] for r in rows]
        #订阅数
        c_sql = '''
             SELECT 
                plugin_id, 
                plugin_name, 
                COUNT(*) as subscribe_count
            FROM subscription
            GROUP BY plugin_id, plugin_name
        '''
        sub = db.session.execute(text(c_sql))
        rows = sub.mappings().all()
        plugin_id_n = {r['plugin_id']: r['subscribe_count'] for r in rows}
        #是否点赞
        sql = '''
            select plugin_id from plugin_like where account_id=:account_id
        '''
        result = db.session.execute(text(sql), {"account_id":user_id})
        rows = result.mappings().all()
        plugin_id_lk = [r['plugin_id'] for r in rows]
        #点赞数
        c_sql = '''
             SELECT 
                plugin_id, 
                plugin_name, 
                COUNT(*) as like_count
            FROM plugin_like
            GROUP BY plugin_id, plugin_name
        '''
        sub = db.session.execute(text(c_sql))
        rows = sub.mappings().all()
        plugin_id_ln = {r['plugin_id']: r['like_count'] for r in rows}

        # result: list[UserToolProvider] = []
        result = {}
        for provider_controller in provider_controllers:
            try:
                # plugin tool
                if hasattr(provider_controller, 'tenant_id'):
                    # convert provider controller to user provider
                    user_builtin_provider = ToolTransformService.builtin_provider_to_user_provider(
                        provider_controller=provider_controller,
                        db_provider=find_provider(provider_controller.entity.identity.name),
                        decrypt_credentials=True
                )
                else:
                    # builtin tool
                    # convert provider controller to user provider
                    user_builtin_provider = ToolTransformService.builtin_provider_to_user_provider(
                        provider_controller=provider_controller,
                        db_provider=find_provider(provider_controller.identity.name),
                        decrypt_credentials=True
                    )

                # add icon
                ToolTransformService.repack_provider(user_builtin_provider, tenant_id)

                tools = provider_controller.get_tools()

                # todo
                for tool in tools or []:
                    user_tool = ToolTransformService.tool_to_user_tool(
                        tenant_id=tenant_id,
                        tool=tool,
                        credentials=user_builtin_provider.original_credentials,
                        labels=ToolLabelManager.get_tool_labels(provider_controller)
                    )
                    user_tool.labels = ToolLabelManager.get_tool_labels_new(user_tool.name)
                    user_tool.create_time = ToolLabelManager.get_tool_create_time(user_tool.name)
                    plugin_id = f"{user_tool.author}&&{user_tool.name}"
                    user_tool.sub = plugin_id in plugin_id_sub
                    user_tool.subscribe_count = plugin_id_n.get(plugin_id, 0)
                    user_tool.lk = plugin_id in plugin_id_lk
                    user_tool.like_count = plugin_id_ln.get(plugin_id, 0)
                    user_builtin_provider.tools.append(user_tool)


                # result.append(user_builtin_provider)
                result[user_builtin_provider.id] = user_builtin_provider
            except Exception as e:
                raise e

        result = list(result.values())
        return BuiltinToolProviderSort.sort(result)
