import json
import uuid

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from agent_platform_basic.extensions.ext_database import async_db
from agent_platform_basic.libs import DbUtils
from agent_platform_basic.models.db_model import Account
from agent_platform_common.configs import agent_platform_config
from agent_platform_core.models.db_model.model import App, Tag, TagBinding, Site
from agent_platform_core.models.db_model.tools import ApiToolProvider
from agent_platform_core.models.enum_model.app_mode import AppMode
from agent_platform_service.fields.app_model_config_async import AppModelConfigAsync


class ApiToolProviderAsync:

    @staticmethod
    async def user_async(db_provider: ApiToolProvider) -> Account:
        async with async_db.AsyncSessionLocal() as session:
            result = await session.execute(select(Account).where(Account.id == db_provider.user_id))
            return result.scalar_one_or_none()

