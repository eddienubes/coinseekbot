from sqlalchemy.ext.asyncio import create_async_engine

from config import config
from .repository import Repository
from .session import session


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
            session_ctx_wrapper=session(PostgresRepo)
        )

    async def on_module_init(self):
        pass

    async def on_module_destroy(self):
        await PostgresRepo.__engine.dispose()
