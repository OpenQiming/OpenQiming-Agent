"""

@Date    ：2024/8/28 11:36 
@Version: 1.0
@Description:

"""
from sqlalchemy import select

from agent_platform_basic.extensions.ext_database import async_db
from agent_platform_basic.models.db_model import Account
from agent_platform_core.models.enum_model.enums import CreatedByRole


class WorkflowRunAsync:

    @classmethod
    async def created_by_account(cls,
                                 created_by: str,
                                 created_by_role: str):
        if created_by_role == CreatedByRole.ACCOUNT.value:
            async with async_db.AsyncSessionLocal() as session:
                result = await session.execute(
                    select(Account).filter(Account.id == created_by)
                )
                return result.scalars().first()
        return None
