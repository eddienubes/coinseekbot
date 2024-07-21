from datetime import datetime

from sqlalchemy import TIMESTAMP, func
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, mapped_column, Mapped


class Base(MappedAsDataclass, DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, init=False, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, init=False, server_default=func.now(), onupdate=func.now(),
                                                 nullable=False)
