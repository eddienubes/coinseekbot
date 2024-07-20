from contextvars import ContextVar

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from config import config
from .database_context import DatabaseContext


class PgEngine:
    def __init__(self):
        self.__engine = create_async_engine(
            f'postgresql+asyncpg://{config.postgres_user}:{config.postgres_pass}@{config.postgres_host}:{config.postgres_port}/{config.postgres_db}',
            echo=True
        )
        self.__factory = async_sessionmaker(expire_on_commit=False)
        self.__ctx: ContextVar[DatabaseContext | None] = ContextVar('pg_ctx', default=None)

    def get_session(self) -> AsyncSession | None:
        """Gets session from the context."""
        db_ctx = self.__ctx.get()
        return db_ctx.session if db_ctx else None

    def try_get_session(self) -> AsyncSession:
        """Tries to get session from the context."""
        session = self.get_session()

        if session is None:
            raise ValueError('You are executing a database operation outside of a session context.')

        return session

    def create_session(self) -> AsyncSession:
        """Creates and sets session in the context."""
        session = self.__factory()

        self.__ctx.set(DatabaseContext(session=session))

        return session

    def delete_session(self) -> None:
        """Deletes session from the context."""
        self.__ctx.set(None)

    async def dispose(self) -> None:
        """Disposes the engine."""
        await self.__engine.dispose()


pg_engine = PgEngine()
