"""

@Date    ：2024/8/28 14:14 
@Version: 1.0
@Description:

"""
from sqlalchemy import select

from agent_platform_basic.extensions.ext_database import async_db
from agent_platform_core.models.enum_model.enums import CreatedByRole


class EndUserAsync:

    @classmethod
    async def created_by_end_user(cls, created_by: str, created_by_role: str):
        from agent_platform_core.models.db_model.model import EndUser
        if created_by_role == CreatedByRole.END_USER:
            async with async_db.AsyncSessionLocal() as session:
                result = await session.execute(
                    select(EndUser).filter(EndUser.id == created_by)
                )
                result = result.scalar_one_or_none()
                return result
        return None
