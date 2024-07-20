from contextvars import ContextVar
from typing import TypeVar, Any, Callable

from . import Base
from .database_context import DatabaseContext
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine, AsyncEngine

# PK/Index type to get entities from the session.
KEY = Any | tuple[Any, ...]


class Repository:
    __GET_T = TypeVar('__GET_T', bound=Base)

    def __init__(self, engine: AsyncEngine,
                 session_ctx_name: str,
                 session_ctx_wrapper: Callable,
                 expire_on_commit: bool = False):

        self.__engine = engine
        self.__ctx: ContextVar[DatabaseContext | None] = ContextVar(session_ctx_name, default=None)
        self.__factory = async_sessionmaker(self.__engine, expire_on_commit=expire_on_commit)

        self.add = session_ctx_wrapper(self.add)
        self.add_all = session_ctx_wrapper(self.add_all)
        self.delete = session_ctx_wrapper(self.delete)
        self.delete_all = session_ctx_wrapper(self.delete_all)
        self.get = session_ctx_wrapper(self.get)

    def add(self, entity: Base) -> None:
        """Adds entity to the session."""
        session = self.try_get_session()
        session.add(entity)

    def add_all(self, entities: list[Base]) -> None:
        """Adds entities to the session."""
        session = self.try_get_session()
        session.add_all(entities)

    def delete(self, entity: Base) -> None:
        """Deletes entity from the session."""
        session = self.try_get_session()
        session.delete(entity)

    def delete_all(self, entities: list[Base]) -> None:
        """Deletes entities from the session."""
        session = self.try_get_session()
        session.delete(entities)

    async def get(self, entity: __GET_T, key: KEY, **kwargs) -> __GET_T | None:
        """Gets entity from the session."""
        session = self.try_get_session()
        return await session.get(entity, ident=key, **kwargs)

    def get_session(self) -> AsyncSession | None:
        """Gets session from the context."""
        db_ctx = self.__ctx.get()
        return db_ctx.session

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

    async def flush(self, session: AsyncSession = None) -> None:
        """Flushes the session."""
        if session is None:
            session = self.get_session()

        if session is None:
            raise ValueError('You are executing flush outside of a session context.')

        await session.flush()

    async def commit(self, session: AsyncSession = None) -> None:
        if session is None:
            session = self.get_session()

        if session is None:
            raise ValueError('You are executing commit outside of a session context.')

        await session.commit()
