from typing import TypeVar, Any

from . import pg_engine
from sqlalchemy.ext.asyncio import AsyncSession
from .base import Base
from .pg_session import pg_session

# PK/Index type to get entities from the session.
KEY = Any | tuple[Any, ...]


class Repository:
    __GET_T = TypeVar('__GET_T')

    @pg_session
    def add(self, entity: Base, session: AsyncSession) -> None:
        """Adds entity to the session."""
        session.add(entity)

    @pg_session
    def add_all(self, entities: list[Base], session: AsyncSession) -> None:
        """Adds entities to the session."""
        session.add_all(entities)

    @pg_session
    def delete(self, entity: Base, session: AsyncSession) -> None:
        """Deletes entity from the session."""
        session.delete(entity)

    @pg_session
    def delete_all(self, entities: list[Base], session: AsyncSession) -> None:
        """Deletes entities from the session."""
        session.delete(entities)

    @pg_session
    async def get(self, entity: __GET_T, key: KEY, session: AsyncSession, **kwargs) -> __GET_T | None:
        """Gets entity from the session."""
        return await session.get(entity, ident=key, **kwargs)

    async def flush(self, session: AsyncSession = None) -> None:
        """Flushes the session."""
        if session is None:
            session = pg_engine.get_session()

        if session is None:
            raise ValueError('You are executing flush outside of a session context.')

        await session.flush()

    async def commit(self, session: AsyncSession = None) -> None:
        if session is None:
            session = pg_engine.get_session()

        if session is None:
            raise ValueError('You are executing commit outside of a session context.')

        await session.commit()
