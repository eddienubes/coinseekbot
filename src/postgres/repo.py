from typing import TypeVar, Any, Type, Sequence, Iterable

from sqlalchemy import delete
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from .session_context import SessionContext
from .base import Base

# PK/Index type to get entities from the session.
KEY = Any | tuple[Any, ...]


class Repo:
    __T = TypeVar('__T', bound=Base)

    def __init__(self, ctx: SessionContext):
        self.__ctx = ctx

        self.add = self.__ctx.wrap(self.add)
        self.add_all = self.__ctx.wrap(self.add_all)
        self.delete = self.__ctx.wrap(self.delete)
        self.delete_all = self.__ctx.wrap(self.delete_all)
        self.get = self.__ctx.wrap(self.get)
        self.merge = self.__ctx.wrap(self.merge)

        # _ methods don't need to be wrapped, as they are not supposed to be used directly.

    async def _insert(self, entity: Type[__T], value: __T) -> __T:
        """Inserts entity to the session.
        Do not use directly
        """
        query = insert(entity).values(value.to_dict()).returning(entity)
        hit_raw = await self.session.execute(query)

        return hit_raw.scalar()

    async def _insert_many(self, entity: Type[__T], values: Iterable[__T]) -> list[__T]:
        """Inserts multiple entities to the session.
        Do not use directly
        """
        if not values:
            return []

        query = insert(entity).values([value.to_dict() for value in values]).returning(entity)
        hits_raw = await self.session.execute(query)

        return list(hits_raw.scalars().all())

    async def _delete_all(self, entity: Type[__T]) -> None:
        """Deletes all records from a table. Non-UoW operation."""
        query = delete(entity).where()
        await self.session.execute(query)

    async def add(self, entity: __T) -> __T:
        """Adds entity to the session."""
        self.session.add(entity)
        return entity

    async def add_all(self, entities: list[__T]) -> list[__T]:
        """Adds entities to the session."""
        self.session.add_all(entities)
        return entities

    async def delete(self, entity: Base) -> None:
        """Deletes entity from the session."""
        await self.session.delete(entity)

    async def delete_all(self, entities: list[Base]) -> None:
        """Deletes entities from the session."""
        await self.session.delete(entities)

    async def get(self, entity: Type[__T], key: KEY, **kwargs) -> __T | None:
        """Gets entity from the session."""
        return await self.session.get(entity, ident=key, **kwargs)

    async def merge(self, entity: Base) -> Base:
        """Merges entity with the session."""
        return await self.session.merge(entity)

    async def flush(self, session: AsyncSession = None) -> None:
        """Flushes the session."""

        ctx = self.__ctx.get_ctx()

        if session is None and ctx is None:
            raise ValueError('You are executing flush outside of a session context.')

        session = session or ctx.session

        await session.flush()

    async def commit(self, session: AsyncSession = None) -> None:
        ctx = self.__ctx.get_ctx()

        if session is None and ctx is None:
            raise ValueError('You are executing commit outside of a session context.')

        session = session or ctx.session

        await session.commit()

    @property
    def session(self) -> AsyncSession:
        return self.__ctx.try_get_ctx().session
