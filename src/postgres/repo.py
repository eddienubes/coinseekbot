from typing import TypeVar, Any

from .session import session
from .pg_engine import pg_engine, PgEngine
from sqlalchemy.ext.asyncio import AsyncSession
from .base import Base

# PK/Index type to get entities from the session.
KEY = Any | tuple[Any, ...]


class Repo:
    __GET_T = TypeVar('__GET_T')

    # TODO: Make pg engine a generic type.
    def __init__(self, engine: PgEngine):
        self.add = session(engine)(self.add)
        self.add_all = session(engine)(self.add_all)
        self.delete = session(engine)(self.delete)
        self.delete_all = session(engine)(self.delete_all)
        self.get = session(engine)(self.get)

    async def add(self, entity: Base, session: AsyncSession) -> None:
        """Adds entity to the session."""
        session.add(entity)

    async def add_all(self, entities: list[Base], session: AsyncSession) -> None:
        """Adds entities to the session."""
        session.add_all(entities)

    async def delete(self, entity: Base, session: AsyncSession) -> None:
        """Deletes entity from the session."""
        await session.delete(entity)

    async def delete_all(self, entities: list[Base], session: AsyncSession) -> None:
        """Deletes entities from the session."""
        await session.delete(entities)

    async def get(self, entity: __GET_T, key: KEY, session: AsyncSession, **kwargs) -> __GET_T | None:
        """Gets entity from the session."""
        return await session.get(entity, ident=key, **kwargs)

    async def flush(self, session: AsyncSession = None) -> None:
        """Flushes the session."""

        ctx = pg_engine.get_ctx()

        if session is None and ctx is None:
            raise ValueError('You are executing flush outside of a session context.')

        session = session or ctx.session

        await session.flush()

    async def commit(self, session: AsyncSession = None) -> None:
        ctx = pg_engine.get_ctx()

        if session is None and ctx is None:
            raise ValueError('You are executing commit outside of a session context.')

        session = session or ctx.session

        await session.commit()
