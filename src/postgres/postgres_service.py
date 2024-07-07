from sqlalchemy.ext.asyncio import create_async_engine

from config import config


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
