import json
import logging
from datetime import datetime
from sqlite3 import IntegrityError
from typing import Optional, Dict

import httpx
from fastapi import Depends, HTTPException
from httpx import get
from sqlalchemy import select, func, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from agent_platform_basic.extensions.ext_database import db, async_db
from agent_platform_basic.libs import DbUtils
from agent_platform_basic.models.db_model.application_audit_share import ApplicationAuditShare
from agent_platform_common.configs import agent_platform_config
from agent_platform_core.model_runtime.utils.encoders import jsonable_encoder
from agent_platform_core.models.db_model.tools import ApiToolProvider, WorkflowToolProvider
from agent_platform_core.models.db_model.workflow import Workflow
from agent_platform_core.models.enum_model.app_status import AppStatus
from agent_platform_core.tools.entities.api_entities import UserTool, UserToolProvider
from agent_platform_core.tools.entities.common_entities import I18nObject
from agent_platform_core.tools.entities.tool_bundle import ApiToolBundle
from agent_platform_core.tools.entities.tool_entities import (
    ApiProviderAuthType,
    ApiProviderSchemaType,
    ToolCredentialsOption,
    ToolProviderCredentials,
)
from agent_platform_core.tools.provider.api_tool_provider import ApiToolProviderController
from agent_platform_core.tools.tool_label_manager import ToolLabelManager
from agent_platform_core.tools.async_tool_label_manager import AsyncToolLabelManager
from agent_platform_core.tools.tool_manager import ToolManager
from agent_platform_core.tools.async_tool_manager import AsyncToolManager
from agent_platform_core.tools.utils.async_tool_transform import AsyncToolTransform
from agent_platform_core.tools.utils.configuration import ToolConfigurationManager
from agent_platform_core.tools.utils.parser import ApiBasedToolSchemaParser
from agent_platform_service.fastapi_fields.resp.console.api_tool_response import ApiToolResponse
from agent_platform_service.fastapi_fields.resp.console.api_tool_test_response import ApiToolTestResponse
from agent_platform_service.services.account_service import TenantService
from agent_platform_service.services.auth.user_permissions_service import UserPermissionsService
from agent_platform_service.services.tools.tools_transform_service import ToolTransformService

logger = logging.getLogger(__name__)


class ApiToolManageService:

    def __init__(self,
                 session: AsyncSession = Depends(DbUtils.get_db_async_session),
                 user_permissions_service: UserPermissionsService = Depends(UserPermissionsService)):
        self.session = session
        self.user_permissions_service = user_permissions_service

    @staticmethod
    def parser_api_schema(schema: str) -> list[ApiToolBundle]:
        """
            parse api schema to tool bundle
        """
        try:
            warnings = {}
            try:
                tool_bundles, schema_type = ApiBasedToolSchemaParser.auto_parse_to_tool_bundle(schema, warning=warnings)
            except Exception as e:
                raise ValueError(f'invalid schema: {str(e)}')

            credentials_schema = [
                ToolProviderCredentials(
                    name='auth_type',
                    type=ToolProviderCredentials.CredentialsType.SELECT,
                    required=True,
                    default='none',
                    options=[
                        ToolCredentialsOption(value='none', label=I18nObject(
                            en_US='None',
                            zh_Hans='无'
                        )),
                        ToolCredentialsOption(value='api_key', label=I18nObject(
                            en_US='Api Key',
                            zh_Hans='Api Key'
                        )),
                    ],
                    placeholder=I18nObject(
                        en_US='Select auth type',
                        zh_Hans='选择认证方式'
                    )
                ),
                ToolProviderCredentials(
                    name='api_key_header',
                    type=ToolProviderCredentials.CredentialsType.TEXT_INPUT,
                    required=False,
                    placeholder=I18nObject(
                        en_US='Enter api key header',
                        zh_Hans='输入 api key header，如：QM-API-KEY'
                    ),
                    default='api_key',
                    help=I18nObject(
                        en_US='HTTP header name for api key',
                        zh_Hans='HTTP 头部字段名，用于传递 api key'
                    )
                ),
                ToolProviderCredentials(
                    name='api_key_value',
                    type=ToolProviderCredentials.CredentialsType.TEXT_INPUT,
                    required=False,
                    placeholder=I18nObject(
                        en_US='Enter api key',
                        zh_Hans='输入 api key'
                    ),
                    default=''
                ),
            ]

            return jsonable_encoder({
                'schema_type': schema_type,
                'parameters_schema': tool_bundles,
                'credentials_schema': credentials_schema,
                'warning': warnings
            })
        except Exception as e:
            raise ValueError(f'invalid schema: {str(e)}')

    @staticmethod
    def convert_schema_to_tool_bundles(schema: str, extra_info: dict = None) -> list[ApiToolBundle]:
        """
            convert schema to tool bundles

            :return: the list of tool bundles, description
        """
        try:
            tool_bundles = ApiBasedToolSchemaParser.auto_parse_to_tool_bundle(schema, extra_info=extra_info)
            return tool_bundles
        except Exception as e:
            raise ValueError(f'invalid schema: {str(e)}')

    async def async_create_api_tool_provider(self, user_id: str, tenant_id: str, provider_name: str, icon: dict,
                                             credentials: dict,
                                             schema_type: str, schema: str, privacy_policy: str, custom_disclaimer: str,
                                             labels: list[str],
                                             header_image: str, access_type: int):
        """
            create api tool provider
        """
        if schema_type not in [member.value for member in ApiProviderSchemaType]:
            raise ValueError(f'invalid schema type {schema}')

        # 用于识别草稿工具数据是否已经进行创建过 tool_api_provider

        # check if the provider exists
        query = await self.session.execute(select(ApiToolProvider).filter(ApiToolProvider.tenant_id == tenant_id,
                                                                          ApiToolProvider.name == provider_name))
        provider: ApiToolProvider = query.scalars().first()

        if provider is not None:
            raise ValueError(f'provider {provider_name} already exists')

        # parse openapi to tool bundle
        extra_info = {}
        # extra info like description will be set here
        tool_bundles, schema_type = ApiToolManageService.convert_schema_to_tool_bundles(schema, extra_info)
        if len(tool_bundles) > 100:
            raise ValueError('the number of apis should be less than 100')

        # create db provider
        db_provider = ApiToolProvider(
            tenant_id=tenant_id,
            user_id=user_id,
            name=provider_name,
            icon=json.dumps(icon, ensure_ascii=False),
            schema=schema,
            description=extra_info.get("description", ""),
            schema_type_str=schema_type,
            tools_str=json.dumps(jsonable_encoder(tool_bundles), ensure_ascii=False),
            credentials_str={},
            privacy_policy=privacy_policy,
            custom_disclaimer=custom_disclaimer,
            version=AppStatus.DRAFT.value,
            status=AppStatus.DRAFT.value,
            access_type=access_type,
            header_image=header_image,
        )

        if 'auth_type' not in credentials:
            raise ValueError('auth_type is required')

        # get auth type, none or api key
        auth_type = ApiProviderAuthType.value_of(credentials['auth_type'])

        # create provider entity
        provider_controller = await ApiToolProviderController.from_db_async(db_provider, auth_type)
        # load tools into provider entity
        provider_controller.load_bundled_tools(tool_bundles)

        # encrypt credentials
        tool_configuration = ToolConfigurationManager(tenant_id=tenant_id, provider_controller=provider_controller)
        encrypted_credentials = tool_configuration.encrypt_tool_credentials(credentials)
        db_provider.credentials_str = json.dumps(encrypted_credentials, ensure_ascii=False)

        self.session.add(db_provider)
        await self.session.commit()
        # update labels
        await AsyncToolLabelManager.update_tool_labels(provider_controller, labels)

        return ApiToolResponse(result="success", provider_id=db_provider.id)

    @staticmethod
    def create_api_tool_provider(
            user_id: str, tenant_id: str, provider_name: str, icon: dict, credentials: dict,
            schema_type: str, schema: str, privacy_policy: str, custom_disclaimer: str, labels: list[str],
            header_image: str,
    ):
        """
            create api tool provider
        """
        if schema_type not in [member.value for member in ApiProviderSchemaType]:
            raise ValueError(f'invalid schema type {schema}')

        # 用于识别草稿工具数据是否已经进行创建过 tool_api_provider

        # check if the provider exists
        provider: ApiToolProvider = db.session.query(ApiToolProvider).filter(
            ApiToolProvider.tenant_id == tenant_id,
            ApiToolProvider.name == provider_name,
        ).first()

        if provider is not None:
            raise ValueError(f'provider {provider_name} already exists')

        # parse openapi to tool bundle
        extra_info = {}
        # extra info like description will be set here
        tool_bundles, schema_type = ApiToolManageService.convert_schema_to_tool_bundles(schema, extra_info)

        if len(tool_bundles) > 100:
            raise ValueError('the number of apis should be less than 100')

        # create db provider
        db_provider = ApiToolProvider(
            tenant_id=tenant_id,
            user_id=user_id,
            name=provider_name,
            icon=json.dumps(icon, ensure_ascii=False),
            schema=schema,
            description=extra_info.get('description', ''),
            schema_type_str=schema_type,
            tools_str=json.dumps(jsonable_encoder(tool_bundles), ensure_ascii=False),
            credentials_str={},
            privacy_policy=privacy_policy,
            version=AppStatus.DRAFT.value,
            custom_disclaimer=custom_disclaimer,
        )

        if 'auth_type' not in credentials:
            raise ValueError('auth_type is required')

        # get auth type, none or api key
        auth_type = ApiProviderAuthType.value_of(credentials['auth_type'])

        # create provider entity
        provider_controller = ApiToolProviderController.from_db(db_provider, auth_type)
        # load tools into provider entity
        provider_controller.load_bundled_tools(tool_bundles)

        # encrypt credentials
        tool_configuration = ToolConfigurationManager(tenant_id=tenant_id, provider_controller=provider_controller)
        encrypted_credentials = tool_configuration.encrypt_tool_credentials(credentials)
        db_provider.credentials_str = json.dumps(encrypted_credentials, ensure_ascii=False)

        db.session.add(db_provider)
        db.session.commit()

        # update labels
        ToolLabelManager.update_tool_labels(provider_controller, labels)

        return {'result': 'success'}

    @staticmethod
    async def async_get_api_tool_provider_remote_schema(
            user_id: str, tenant_id: str, url: str
    ):
        """
            get api tool provider remote schema
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "Accept": "*/*",
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                raise ValueError(f'Got status code {response.status_code}')
            schema = response.text

            # try to parse schema, avoid SSRF attack
            ApiToolManageService.parser_api_schema(schema)
        except Exception as e:
            logger.error(f"parse api schema error: {str(e)}")
            raise ValueError('invalid schema, please check the url you provided')

        return {
            'schema': schema
        }

    @staticmethod
    def get_api_tool_provider_remote_schema(
            user_id: str, tenant_id: str, url: str
    ):
        """
            get api tool provider remote schema
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "Accept": "*/*",
        }

        try:
            response = get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                raise ValueError(f'Got status code {response.status_code}')
            schema = response.text

            # try to parse schema, avoid SSRF attack
            ApiToolManageService.parser_api_schema(schema)
        except Exception as e:
            logger.error(f"parse api schema error: {str(e)}")
            raise ValueError('invalid schema, please check the url you provided')

        return {
            'schema': schema
        }

    @staticmethod
    async def async_list_api_tool_provider_tools(
            user_id: str, tenant_id: str, provider: str
    ) -> list[UserTool]:
        """
            list api tool provider tools
        """

        async with async_db.AsyncSessionLocal() as session:
            query = await session.execute(select(ApiToolProvider).filter(ApiToolProvider.tenant_id == tenant_id,
                                                                         ApiToolProvider.name == provider))
            provider: ApiToolProvider = query.scalars().first()

        if provider is None:
            raise ValueError(f'you have not added provider {provider}')

        controller = await AsyncToolTransform.api_provider_to_controller(db_provider=provider)
        labels = await AsyncToolLabelManager.get_tool_labels(controller)

        return [
            ToolTransformService.tool_to_user_tool(
                tool_bundle,
                labels=labels,
            ) for tool_bundle in provider.tools
        ]

    @staticmethod
    def list_api_tool_provider_tools(
            user_id: str, tenant_id: str, provider: str
    ) -> list[UserTool]:
        """
            list api tool provider tools
        """
        provider: ApiToolProvider = db.session.query(ApiToolProvider).filter(
            ApiToolProvider.tenant_id == tenant_id,
            ApiToolProvider.name == provider,
        ).first()

        if provider is None:
            raise ValueError(f'you have not added provider {provider}')

        controller = ToolTransformService.api_provider_to_controller(db_provider=provider)
        labels = ToolLabelManager.get_tool_labels(controller)

        return [
            ToolTransformService.tool_to_user_tool(
                tool_bundle,
                labels=labels,
            ) for tool_bundle in provider.tools
        ]

    async def async_update_api_tool_provider(self,
                                             user_id: str, tenant_id: str, provider_name: str, original_provider: str,
                                             icon: dict, credentials: dict,
                                             schema_type: str, schema: str, privacy_policy: str, custom_disclaimer: str,
                                             labels: list[str], access_type: int
                                             ):
        """
            update api tool provider
        """

        if schema_type not in [member.value for member in ApiProviderSchemaType]:
            raise ValueError(f'invalid schema type {schema}')

        provider_name = provider_name.strip()

        # check if the provider exists
        query = await self.session.execute(select(ApiToolProvider).filter(ApiToolProvider.tenant_id == tenant_id,
                                                                          ApiToolProvider.name == provider_name,
                                                                          ApiToolProvider.version == AppStatus.DRAFT.value))
        provider: ApiToolProvider = query.scalars().first()

        if provider is None:
            raise Exception(f'api provider {provider_name} does not exists')

        # parse openapi to tool bundle
        extra_info = {}
        # extra info like description will be set here
        tool_bundles, schema_type = ApiToolManageService.convert_schema_to_tool_bundles(schema, extra_info)

        # update db provider
        provider.name = provider_name
        provider.icon = json.dumps(icon, ensure_ascii=False)
        provider.schema = schema
        provider.description = extra_info.get('description', '')
        provider.schema_type_str = ApiProviderSchemaType.OPENAPI.value
        provider.tools_str = json.dumps(jsonable_encoder(tool_bundles), ensure_ascii=False)
        provider.privacy_policy = privacy_policy
        provider.custom_disclaimer = custom_disclaimer
        provider.access_type = access_type

        if 'auth_type' not in credentials:
            raise ValueError('auth_type is required')

        # get auth type, none or api key
        auth_type = ApiProviderAuthType.value_of(credentials['auth_type'])

        # create provider entity
        provider_controller = await ApiToolProviderController.from_db_async(provider, auth_type)
        # load tools into provider entity
        provider_controller.load_bundled_tools(tool_bundles)

        # get original credentials if exists
        tool_configuration = ToolConfigurationManager(tenant_id=tenant_id, provider_controller=provider_controller)

        original_credentials = tool_configuration.decrypt_tool_credentials(provider.credentials)
        masked_credentials = tool_configuration.mask_tool_credentials(original_credentials)
        # check if the credential has changed, save the original credential
        for name, value in credentials.items():
            if name in masked_credentials and value == masked_credentials[name]:
                credentials[name] = original_credentials[name]

        credentials = tool_configuration.encrypt_tool_credentials(credentials)
        provider.credentials_str = json.dumps(credentials, ensure_ascii=False)

        self.session.add(provider)
        await self.session.commit()
        # delete cache
        tool_configuration.delete_tool_credentials_cache()

        # update labels
        await AsyncToolLabelManager.update_tool_labels(provider_controller, labels)

        return ApiToolResponse(result="success", provider_id=provider.id)

    @staticmethod
    def update_api_tool_provider(
            user_id: str, tenant_id: str, provider_name: str, original_provider: str, icon: dict, credentials: dict,
            schema_type: str, schema: str, privacy_policy: str, custom_disclaimer: str, labels: list[str]
    ):
        """
            update api tool provider
        """

        # def get_prefix_before_last_underscore(name: str) -> str:
        #     parts = name.rsplit('_', 1)
        #     return parts[0]

        if schema_type not in [member.value for member in ApiProviderSchemaType]:
            raise ValueError(f'invalid schema type {schema}')

        # check if the provider exists
        provider: ApiToolProvider = db.session.query(ApiToolProvider).filter(
            ApiToolProvider.tenant_id == tenant_id,
            ApiToolProvider.name == original_provider,
            ApiToolProvider.version == AppStatus.DRAFT.value
        ).first()

        if provider is None:
            raise ValueError(f'api provider {provider_name} does not exists')

        # parse openapi to tool bundle
        extra_info = {}
        # extra info like description will be set here
        tool_bundles, schema_type = ApiToolManageService.convert_schema_to_tool_bundles(schema, extra_info)

        # update db provider
        provider.name = provider_name
        provider.icon = json.dumps(icon, ensure_ascii=False)
        provider.schema = schema
        provider.description = extra_info.get('description', '')
        provider.schema_type_str = ApiProviderSchemaType.OPENAPI.value
        provider.tools_str = json.dumps(jsonable_encoder(tool_bundles), ensure_ascii=False)
        provider.privacy_policy = privacy_policy
        provider.custom_disclaimer = custom_disclaimer

        if 'auth_type' not in credentials:
            raise ValueError('auth_type is required')

        # get auth type, none or api key
        auth_type = ApiProviderAuthType.value_of(credentials['auth_type'])

        # create provider entity
        provider_controller = ApiToolProviderController.from_db(provider, auth_type)
        # load tools into provider entity
        provider_controller.load_bundled_tools(tool_bundles)

        # get original credentials if exists
        tool_configuration = ToolConfigurationManager(tenant_id=tenant_id, provider_controller=provider_controller)

        original_credentials = tool_configuration.decrypt_tool_credentials(provider.credentials)
        masked_credentials = tool_configuration.mask_tool_credentials(original_credentials)
        # check if the credential has changed, save the original credential
        for name, value in credentials.items():
            if name in masked_credentials and value == masked_credentials[name]:
                credentials[name] = original_credentials[name]

        credentials = tool_configuration.encrypt_tool_credentials(credentials)
        provider.credentials_str = json.dumps(credentials, ensure_ascii=False)

        db.session.add(provider)
        db.session.commit()

        # delete cache
        tool_configuration.delete_tool_credentials_cache()

        # update labels
        ToolLabelManager.update_tool_labels(provider_controller, labels)

        return {'result': 'success'}

    # @staticmethod
    def published_api_tool_provider(
            user_id: str, tenant_id: str, provider_name: str
    ):
        """
            published tool provider and set tool app
        """

        draft_provider: ApiToolProvider = db.session.query(ApiToolProvider).filter(
            ApiToolProvider.tenant_id == tenant_id,
            ApiToolProvider.name == provider_name,
            ApiToolProvider.version == AppStatus.DRAFT.value
        ).first()

        if draft_provider is None:
            raise ValueError(f'you not have draft api provider {provider_name}')

        current_version = str(datetime.now().replace(tzinfo=None))

        new_version_api_provider = ApiToolProvider(
            tenant_id=tenant_id,
            user_id=user_id,
            name=provider_name + "_" + current_version,
            icon=draft_provider.icon,
            schema=draft_provider.schema,
            description=draft_provider.description,
            schema_type_str=draft_provider.schema_type_str,
            tools_str=draft_provider.tools_str,
            credentials_str=draft_provider.credentials_str,
            privacy_policy=draft_provider.privacy_policy,
            custom_disclaimer=draft_provider.custom_disclaimer,
            version=current_version,
            status=AppStatus.PUBLISHED.value,
            header_image=draft_provider.header_image,
        )

        db.session.add(new_version_api_provider)
        db.session.commit()
        return {'result': 'success'}

    @staticmethod
    async def async_delete_api_tool_provider(
            tenant_id: str, provider_name: str
    ):
        """
            delete tool provider
        """
        async with async_db.AsyncSessionLocal() as session:
            query = await session.execute(select(ApiToolProvider).filter(
                ApiToolProvider.name == provider_name,
                ApiToolProvider.tenant_id == tenant_id
                # ApiToolProvider.version == AppStatus.DRAFT.value 发布和草稿都调用的这个接口
            ))
            provider: ApiToolProvider = query.scalars().first()


            if provider is None:
                raise ValueError(f'you have not added provider {provider_name}')

            if provider.status == AppStatus.PUBLISHED.value:
                # 判断是否被引用

                query = await session.execute(
                    select(func.count(Workflow.id)).filter(Workflow.graph.like(f"%{provider.id}%")))
                used_counts = query.scalar()
                if used_counts > 0:
                    return {'result': 'error', 'msg': '该插件已经被引用，无法进行删除'}

            await session.delete(provider)
            await session.commit()

        return {'result': 'success'}

    async def delete_api_tool_provider_by_provider_name(self, provider_name: str) -> Dict[str, str]:
        try:
            # 查询 ApiToolProvider
            provider: Optional[ApiToolProvider] = (
                await self.session.execute(
                    select(ApiToolProvider).where(ApiToolProvider.name == provider_name)
                )
            ).scalar_one_or_none()

            if provider is None:
                raise ValueError(f'you have not added provider {provider_name}')

            await self.session.delete(provider)  # 删除操作不会阻塞
            await self.session.commit()
            return {'result': 'success'}

        except IntegrityError as e:
            # 回滚事务
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")

    @staticmethod
    async def async_get_api_tool_provider(
            user_id: str, tenant_id: str, provider: str):
        return await AsyncToolManager.user_get_api_provider(provider=provider, tenant_id=tenant_id)

    @staticmethod
    def get_api_tool_provider(
            user_id: str, tenant_id: str, provider: str
    ):
        """
            get api tool provider
        """
        return ToolManager.user_get_api_provider(provider=provider, tenant_id=tenant_id)

    async def async_test_api_tool_preview(self, tenant_id: str,
                                          provider_name: str,
                                          tool_name: str,
                                          credentials: dict,
                                          parameters: dict,
                                          schema_type: str,
                                          schema: str):
        """
            test api tool before adding api tool provider
        """
        if schema_type not in [member.value for member in ApiProviderSchemaType]:
            raise ValueError(f'invalid schema type {schema_type}')

        try:
            tool_bundles, _ = ApiBasedToolSchemaParser.auto_parse_to_tool_bundle(schema)
        except Exception as e:
            raise ValueError('invalid schema')

        # get tool bundle
        tool_bundle = next(filter(lambda tb: tb.operation_id == tool_name, tool_bundles), None)
        if tool_bundle is None:
            raise ValueError(f'invalid tool name {tool_name}')

        # query = await self.session.execute(select(ApiToolProvider).filter(ApiToolProvider.tenant_id == tenant_id,
        #                                                                   ApiToolProvider.name == provider_name))
        # 更改查询条件，ApiToolProvider.name 改为tool_name
        query = await self.session.execute(select(ApiToolProvider).filter(ApiToolProvider.tenant_id == tenant_id,
                                                                          ApiToolProvider.name == tool_name))
        db_provider: ApiToolProvider = query.scalars().first()

        if not db_provider:
            # create a fake db provider
            db_provider = ApiToolProvider(
                tenant_id='', user_id='', name='', icon='',
                schema=schema,
                description='',
                schema_type_str=ApiProviderSchemaType.OPENAPI.value,
                tools_str=json.dumps(jsonable_encoder(tool_bundles), ensure_ascii=False),
                credentials_str=json.dumps(credentials, ensure_ascii=False),
            )

        if 'auth_type' not in credentials:
            raise ValueError('auth_type is required')

        # get auth type, none or api key
        auth_type = ApiProviderAuthType.value_of(credentials['auth_type'])

        # create provider entity
        provider_controller = await ApiToolProviderController.from_db_async(db_provider, auth_type)
        # load tools into provider entity
        provider_controller.load_bundled_tools(tool_bundles)

        # decrypt credentials
        if db_provider.id:
            tool_configuration = ToolConfigurationManager(
                tenant_id=tenant_id,
                provider_controller=provider_controller
            )
            decrypted_credentials = tool_configuration.decrypt_tool_credentials(credentials)
            # check if the credential has changed, save the original credential
            masked_credentials = tool_configuration.mask_tool_credentials(decrypted_credentials)
            for name, value in credentials.items():
                if name in masked_credentials and value == masked_credentials[name]:
                    credentials[name] = decrypted_credentials[name]

        try:
            # provider_controller.validate_credentials_format(credentials)
            # get tool
            tool = provider_controller.get_tool(tool_name)
            tool = tool.fork_tool_runtime(runtime={
                'credentials': credentials,
                'tenant_id': tenant_id,
            })
            if db_provider.access_type == 1:   # 能力平台接入
                result = await tool.async_validate_decoos_credentials(credentials, parameters)
            elif db_provider.access_type == 2: # 其他平台接入
                result = await tool.async_validate_credentials(credentials)
            # result = await tool.async_validate_credentials(credentials, parameters)  # 原来的
        except Exception as e:
            return ApiToolTestResponse(error=str(e))

        return ApiToolTestResponse(result=result)

    @staticmethod
    def test_api_tool_preview(
            tenant_id: str,
            provider_name: str,
            tool_name: str,
            credentials: dict,
            parameters: dict,
            schema_type: str,
            schema: str
    ):
        """
            test api tool before adding api tool provider
        """
        if schema_type not in [member.value for member in ApiProviderSchemaType]:
            raise ValueError(f'invalid schema type {schema_type}')

        try:
            tool_bundles, _ = ApiBasedToolSchemaParser.auto_parse_to_tool_bundle(schema)
        except Exception as e:
            raise ValueError('invalid schema')

        # get tool bundle
        tool_bundle = next(filter(lambda tb: tb.operation_id == tool_name, tool_bundles), None)
        if tool_bundle is None:
            raise ValueError(f'invalid tool name {tool_name}')

        db_provider: ApiToolProvider = db.session.query(ApiToolProvider).filter(
            ApiToolProvider.tenant_id == tenant_id,
            ApiToolProvider.name == provider_name,
        ).first()

        if not db_provider:
            # create a fake db provider
            db_provider = ApiToolProvider(
                tenant_id='', user_id='', name='', icon='',
                schema=schema,
                description='',
                schema_type_str=ApiProviderSchemaType.OPENAPI.value,
                tools_str=json.dumps(jsonable_encoder(tool_bundles), ensure_ascii=False),
                credentials_str=json.dumps(credentials),
            )

        if 'auth_type' not in credentials:
            raise ValueError('auth_type is required')

        # get auth type, none or api key
        auth_type = ApiProviderAuthType.value_of(credentials['auth_type'])

        # create provider entity
        provider_controller = ApiToolProviderController.from_db(db_provider, auth_type)
        # load tools into provider entity
        provider_controller.load_bundled_tools(tool_bundles)

        # decrypt credentials
        if db_provider.id:
            tool_configuration = ToolConfigurationManager(
                tenant_id=tenant_id,
                provider_controller=provider_controller
            )
            decrypted_credentials = tool_configuration.decrypt_tool_credentials(credentials)
            # check if the credential has changed, save the original credential
            masked_credentials = tool_configuration.mask_tool_credentials(decrypted_credentials)
            for name, value in credentials.items():
                if name in masked_credentials and value == masked_credentials[name]:
                    credentials[name] = decrypted_credentials[name]

        try:
            # provider_controller.validate_credentials_format(credentials)
            # get tool
            tool = provider_controller.get_tool(tool_name)
            tool = tool.fork_tool_runtime(runtime={
                'credentials': credentials,
                'tenant_id': tenant_id,
            })
            result = tool.validate_credentials(credentials, parameters)
        except Exception as e:
            return {'error': str(e)}

        return {'result': result or 'empty response'}

    @staticmethod
    def list_api_tools(
            user_id: str, tenant_id: str, status: str = None
    ) -> list[UserToolProvider]:
        """
            list api tools
        """
        # get all api providers
        filters = []
        tenant_id = [tenant_id, agent_platform_config.GLOBAL_TENANT_ID]   # 原来的，感觉两个tenant_id有问题
        # tenant_id = [agent_platform_config.GLOBAL_TENANT_ID]
        filters.append(ApiToolProvider.tenant_id.in_(tenant_id))
        if status:
            filters.append(ApiToolProvider.status == status)
        db_providers: list[ApiToolProvider] = db.session.query(ApiToolProvider).filter(
            *filters
        ).all() or []

        result: list[UserToolProvider] = []

        #是否订阅
        sql = '''
            select plugin_id from subscription where account_id=:account_id
        '''
        sub = db.session.execute(text(sql), {"account_id":user_id})
        rows = sub.mappings().all()
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
        lk = db.session.execute(text(sql), {"account_id":user_id})
        rows = lk.mappings().all()
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

        for provider in db_providers:
            # convert provider controller to user provider
            provider_controller = ToolTransformService.api_provider_to_controller(db_provider=provider)
            labels = ToolLabelManager.get_tool_labels(provider_controller)
            labels = ["通用"]
            user_provider = ToolTransformService.api_provider_to_user_provider(
                provider_controller,
                db_provider=provider,
                decrypt_credentials=True
            )

            # add icon
            ToolTransformService.repack_provider(user_provider)

            # tools = provider_controller.get_tools(
            #     user_id=user_id, tenant_id=tenant_id
            # )
            tools = []
            for t_id in tenant_id:
                tool = provider_controller.get_tools(
                    user_id=user_id, tenant_id=t_id
                )
                tools.extend(tool)

            for tool in tools:
                for t_id in tenant_id:
                    user_tool = ToolTransformService.tool_to_user_tool(
                        tenant_id=t_id,
                        tool=tool,
                        credentials=user_provider.original_credentials,
                        labels=labels
                    )
                    if user_tool not in user_provider.tools:
                        user_provider.tools.append(user_tool)
                    user_tool.create_time = user_provider.created_time
                    plugin_id = f"{user_tool.author}&&{user_tool.name}"
                    user_tool.sub = plugin_id in plugin_id_sub
                    user_tool.subscribe_count = plugin_id_n.get(plugin_id, 0)
                    user_tool.lk = plugin_id in plugin_id_lk
                    user_tool.like_count = plugin_id_ln.get(plugin_id, 0)

            result.append(user_provider)

        return result

    @staticmethod
    def list_api_share_tools(
            user_id: str, tenant_id: str, status: str = None
    ) -> list[UserToolProvider]:
        """
            list api tools
        """
        # get all api providers
        result = db.session.execute(select(ApplicationAuditShare.app_id))
        app_ids = result.scalars().all()
        ids_list = [id for id in app_ids]
        logger.info("======================test ttttttttttt================")
        logger.info(ids_list)

        filters = []
        filters.append(ApiToolProvider.id.in_(ids_list))

        tenant_id = [tenant_id, agent_platform_config.GLOBAL_SHARE_TENANT_ID]
        # # tenant_id = [agent_platform_config.GLOBAL_TENANT_ID]
        # filters.append(ApiToolProvider.tenant_id.in_(tenant_id))
        if status:
            filters.append(ApiToolProvider.status == status)
        db_providers: list[ApiToolProvider] = db.session.query(ApiToolProvider).filter(
            *filters
        ).all() or []

        result: list[UserToolProvider] = []

        for provider in db_providers:
            # convert provider controller to user provider
            provider_controller = ToolTransformService.api_provider_to_controller(db_provider=provider)
            labels = ToolLabelManager.get_tool_labels(provider_controller)
            user_provider = ToolTransformService.api_provider_to_user_provider(
                provider_controller,
                db_provider=provider,
                decrypt_credentials=True
            )

            # add icon
            ToolTransformService.repack_provider(user_provider)

            # tools = provider_controller.get_tools(
            #     user_id=user_id, tenant_id=tenant_id
            # )
            tools = []
            for t_id in tenant_id:
                tool = provider_controller.get_tools(
                    user_id=user_id, tenant_id=t_id
                )
                tools.extend(tool)

            for tool in tools:
                for t_id in tenant_id:
                    user_tool = ToolTransformService.tool_to_user_tool(
                        tenant_id=t_id,
                        tool=tool,
                        credentials=user_provider.original_credentials,
                        labels=labels
                    )
                    if user_tool not in user_provider.tools:
                        user_provider.tools.append(user_tool)

            result.append(user_provider)

        return result

    async def check_workflow_tool_name_repeat(self, tenant_id: str, name: str, app_id: str):
        exists_count = await self.session.scalar(select(func.count()).select_from(WorkflowToolProvider).filter(
            WorkflowToolProvider.tenant_id.in_([tenant_id, agent_platform_config.GLOBAL_TENANT_ID]),
            # name or app_id
            or_(WorkflowToolProvider.name == name, WorkflowToolProvider.app_id == app_id)
        ))
        return exists_count > 0
