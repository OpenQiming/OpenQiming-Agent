import json
import uuid
from typing import Optional

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from agent_platform_basic.libs import DbUtils
from agent_platform_common.configs import agent_platform_config
from agent_platform_core.models.db_model.model import App, Tag, TagBinding, Site, AppModelConfig
from agent_platform_core.models.db_model.tools import ApiToolProvider
from agent_platform_core.models.enum_model.app_mode import AppMode
from agent_platform_service.fields.app_model_config_async import AppModelConfigAsync


class AppAsync:
    def __init__(self,
                 session: AsyncSession = Depends(DbUtils.get_db_async_session),
                 _model_config_async: AppModelConfigAsync = Depends(AppModelConfigAsync)):
        self.session = session
        self._model_config_async = _model_config_async

    async def app_model_config_async_marshal(self, app: App):
        model_config = await self._model_config_async.get_app_model_config(app)
        if model_config:
            return {'pre_prompt': model_config.pre_prompt,
                    'model': json.loads(model_config.model) if model_config.model else None}
        return None

    async def tags_async(self, app: App):
        tags = await self.session.execute(select(Tag).join(
            TagBinding,
            Tag.id == TagBinding.tag_id
        ).filter(
            TagBinding.target_id == app.id,
            TagBinding.tenant_id == app.tenant_id,
            Tag.tenant_id == app.tenant_id,
            Tag.type == 'app'
        ))

        return tags.scalars().all() if tags.scalars().all() else []

    async def mode_compatible_with_agent_async(self, app: App) -> str:
        if app.mode == AppMode.CHAT.value and await self.is_agent_async(app):
            return AppMode.AGENT_CHAT.value

        return app.mode

    async def is_agent_async(self, app: App) -> bool:
        app_model_config = await self._model_config_async.get_app_model_config(app)
        if not app_model_config:
            return False
        if not app_model_config.agent_mode:
            return False
        if self._model_config_async.agent_mode_dict(app_model_config).get('enabled', False) \
                and self._model_config_async.agent_mode_dict(app_model_config).get('strategy', '') in [
            'function_call', 'react']:
            app.mode = AppMode.AGENT_CHAT.value
            await self.session.commit()
            return True
        return False

    async def model_config_fields_async(self, app: App):
        app_model_config = await self._model_config_async.get_app_model_config(app)
        return await self._model_config_async.get_model_config_fields_async(app_model_config)

    async def site_fields_async(self, app: App):
        site = await self.session.execute(select(Site).filter(Site.app_id == app.id))
        site = site.scalar_one_or_none()

        app_base_url = agent_platform_config.APP_WEB_URL
        return {
            'access_token': site.code,
            'code': site.code,
            'title': site.title,
            'icon': site.icon,
            'icon_background': site.icon_background,
            'description': site.description,
            'default_language': site.default_language,
            'chat_color_theme': site.chat_color_theme,
            'chat_color_theme_inverted': site.chat_color_theme_inverted,
            'customize_domain': site.customize_domain,
            'copyright': site.copyright,
            'privacy_policy': site.privacy_policy,
            'custom_disclaimer': site.customize_domain,
            'customize_token_strategy': site.customize_token_strategy,
            'prompt_public': site.prompt_public,
            'app_base_url': app_base_url,
            'show_workflow_steps': site.show_workflow_steps,
        }

    async def deleted_tools_async(self, app):
        # get agent mode tools
        app_model_config = await self._model_config_async.get_app_model_config(app)
        if not (app_model_config and app_model_config.agent_mode):
            return []
        agent_mode = self._model_config_async.agent_mode_dict(app_model_config)
        tools = agent_mode.get('tools', [])

        provider_ids = [
            tool.get('provider_id')
            for tool in tools
            if
            len(tool.keys()) >= 4 and tool.get('provider_type') == 'api' and self.is_valid_uuid(tool.get('provider_id'))
        ]

        if not provider_ids:
            return []

        api_providers = await self.session.execute(select(ApiToolProvider).where(ApiToolProvider.id.in_(provider_ids)))
        current_api_provider_ids = {str(api_provider.id) for api_provider in api_providers.scalars().all()}

        # 过滤出已删除的工具
        deleted_tools = [
            tool['tool_name']
            for tool in tools
            if tool.get('provider_type') == 'api' and tool.get('provider_id') not in current_api_provider_ids
        ]

        return deleted_tools

    async def draft_app_model_config(self, app) -> Optional['AppModelConfig']:
        app_model_config = await self.session.execute(select(AppModelConfig).filter(AppModelConfig.id == app.app_model_config_id))
        app_model_config = app_model_config.scalars().first()
        return app_model_config

    @staticmethod
    def is_valid_uuid(val):
        try:
            uuid.UUID(val)
            return True
        except ValueError:
            return False
