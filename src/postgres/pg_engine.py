import logging

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from config import config


class PgEngine:
    def __init__(self):
        self.__engine = create_async_engine(
            f'postgresql+asyncpg://{config.postgres_user}:{config.postgres_pass}@{config.postgres_host}:{config.postgres_port}/{config.postgres_db}'
        )
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

        self.__factory = async_sessionmaker(bind=self.__engine, expire_on_commit=False)

    def create_session(self) -> AsyncSession:
        """Creates a new session."""
        return self.__factory()

    async def dispose(self) -> None:
        """Disposes the engine."""
        await self.__engine.dispose()


pg_engine = PgEngine()
