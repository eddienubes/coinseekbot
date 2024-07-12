from sqlalchemy import TIMESTAMP, func
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base, mapped_column

from config import config


class Base(declarative_base()):
    created_at = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)


class PostgresService:
    def __init__(self):
        url = f'postgresql+asyncpg://{config.postgres_user}:{config.postgres_pass}@{config.postgres_host}:{config.postgres_port}/{config.postgres_db}'
        self.__engine = create_async_engine(
            url,
            echo=True
        )

    async def on_module_init(self):
        pass

    async def on_module_destroy(self):
        if not self.__engine:
            raise Exception('Engine is not initialized')

        await self.__engine.dispose()
