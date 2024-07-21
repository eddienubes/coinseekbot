from contextvars import ContextVar, Context, copy_context

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from config import config
from .database_context import DatabaseContext


class PgEngine:
    def __init__(self):
        self.__engine = create_async_engine(
            f'postgresql+asyncpg://{config.postgres_user}:{config.postgres_pass}@{config.postgres_host}:{config.postgres_port}/{config.postgres_db}',
            echo=True
        )
        self.__factory = async_sessionmaker(bind=self.__engine, expire_on_commit=False)
        self.__ctx: ContextVar[DatabaseContext | None] = ContextVar('pg_ctx', default=None)

    def get_ctx(self) -> DatabaseContext | None:
        """Gets current database context."""
        db_ctx = self.__ctx.get()
        return db_ctx

    def try_get_ctx(self) -> DatabaseContext:
        """Tries to get current database context."""
        ctx = self.get_ctx()

        if ctx is None:
            raise ValueError('You are executing a database operation outside of a session context.')

        return ctx

    def set_ctx(self, fn_name: str = None) -> DatabaseContext:
        """Creates and returns database execution context."""
        session = self.__factory()

        ctx = DatabaseContext(session=session)

        self.__ctx.set(DatabaseContext(session=session, fn_name=fn_name))

        return ctx

    def delete_session(self) -> None:
        """Deletes session from the context."""
        self.__ctx.set(None)

    async def dispose(self) -> None:
        """Disposes the engine."""
        await self.__engine.dispose(close=True)


pg_engine = PgEngine()
