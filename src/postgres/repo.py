from typing import TypeVar, Any
from sqlalchemy.ext.asyncio import AsyncSession

from .session_context import SessionContext
from .base import Base

# PK/Index type to get entities from the session.
KEY = Any | tuple[Any, ...]


class Repo:
    __GET_T = TypeVar('__GET_T')

    def __init__(self, ctx: SessionContext):
        self.__ctx = ctx

    async def add(self, entity: Base) -> None:
        """Adds entity to the session."""
        self.session.add(entity)

    async def add_all(self, entities: list[Base]) -> None:
        """Adds entities to the session."""
        self.session.add_all(entities)

    async def delete(self, entity: Base) -> None:
        """Deletes entity from the session."""
        await self.session.delete(entity)

    async def delete_all(self, entities: list[Base]) -> None:
        """Deletes entities from the session."""
        await self.session.delete(entities)

    async def get(self, entity: __GET_T, key: KEY, **kwargs) -> __GET_T | None:
        """Gets entity from the session."""
        return await self.session.get(entity, ident=key, **kwargs)

    async def flush(self, session: AsyncSession) -> None:
        """Flushes the session."""

        ctx = self.__ctx.get_ctx()

        if session is None and ctx is None:
            raise ValueError('You are executing flush outside of a session context.')

        session = session or ctx.session

        await session.flush()

    async def commit(self, session: AsyncSession) -> None:
        ctx = self.__ctx.get_ctx()

        if session is None and ctx is None:
            raise ValueError('You are executing commit outside of a session context.')

        session = session or ctx.session

        await session.commit()

    @property
    def session(self) -> AsyncSession:
        return self.__ctx.get_or_create_ctx().session
