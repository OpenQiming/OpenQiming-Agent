from sqlalchemy.ext.asyncio import AsyncSession
from agent_platform_basic.extensions.ext_database import async_db


class DbUtils:

    @staticmethod
    def duplicate_record(record):
        # 获取要复制的记录
        if not record:
            return None

        # 创建一个新的实例，并复制所有字段
        record_dict = record.__dict__.copy()
        record_dict.pop('_sa_instance_state')  # 移除 SQLAlchemy 的内部状态
        record_dict.pop('id')

        # 创建新记录
        new_record = record.__class__(**record_dict)

        return new_record

    @staticmethod
    # 获取异步会话
    async def get_db_async_session() -> AsyncSession:
        async with async_db.AsyncSessionLocal() as session:
            yield session

    @staticmethod
    # 获取共享数据库异步会话
    async def get_db_async_share_session() -> AsyncSession:
        async with async_db.AsyncShareSessionLocal() as session:
            yield session