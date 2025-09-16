from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base

db = SQLAlchemy()


def init_app(app):
    db.init_app(app)


Base = declarative_base()


class AsyncDb:
    engine = None
    share_engine = None
    AsyncSessionLocal = None
    AsyncShareSessionLocal = None


async_db = AsyncDb()


def init_fastapi(fastapi_app):
    async_db.engine = create_async_engine(
        url=fastapi_app.state.config.get("SQLALCHEMY_ASYNC_DATABASE_URI"),
        pool_size=fastapi_app.state.config.get("SQLALCHEMY_POOL_SIZE"),
        max_overflow=fastapi_app.state.config.get("SQLALCHEMY_MAX_OVERFLOW"),
        pool_recycle=fastapi_app.state.config.get("SQLALCHEMY_POOL_RECYCLE"),
        pool_pre_ping=fastapi_app.state.config.get("SQLALCHEMY_POOL_PRE_PING"),
        echo=fastapi_app.state.config.get("SQLALCHEMY_ECHO"),
    )
    async_db.AsyncSessionLocal = async_sessionmaker(
        bind=async_db.engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async_db.share_engine = create_async_engine(
        url='postgresql+asyncpg://agent_platform:zOb4#eI&0%5!@172.27.221.54:29338/agent_test',
        pool_size=fastapi_app.state.config.get("SQLALCHEMY_POOL_SIZE"),
        max_overflow=fastapi_app.state.config.get("SQLALCHEMY_MAX_OVERFLOW"),
        pool_recycle=fastapi_app.state.config.get("SQLALCHEMY_POOL_RECYCLE"),
        pool_pre_ping=fastapi_app.state.config.get("SQLALCHEMY_POOL_PRE_PING"),
        echo=fastapi_app.state.config.get("SQLALCHEMY_ECHO"),
    )
    async_db.AsyncShareSessionLocal = async_sessionmaker(
        bind=async_db.share_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
