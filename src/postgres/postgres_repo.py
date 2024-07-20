from sqlalchemy import TIMESTAMP, func
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, mapped_column

from config import config
from postgres.repository import Repository
from .session import pg_session


class Base(DeclarativeBase, MappedAsDataclass):
    created_at = mapped_column(TIMESTAMP, init=False, server_default=func.now(), nullable=False)
    updated_at = mapped_column(TIMESTAMP, init=False, server_default=func.now(), onupdate=func.now(), nullable=False)


class PostgresRepo(Repository):
    __engine = create_async_engine(
        f'postgresql+asyncpg://{config.postgres_user}:{config.postgres_pass}@{config.postgres_host}:{config.postgres_port}/{config.postgres_db}',
        echo=True
    )

    def __init__(self):
        super().__init__(
            engine=PostgresRepo.__engine,
            session_ctx_name='pg_session_ctx',
            expire_on_commit=False,
            session_ctx_wrapper=pg_session
        )

    async def on_module_init(self):
        pass

    async def on_module_destroy(self):
        await PostgresRepo.__engine.dispose()
