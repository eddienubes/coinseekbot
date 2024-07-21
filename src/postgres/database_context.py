from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class DatabaseContext:
    session: AsyncSession
    fn_name: str = None
