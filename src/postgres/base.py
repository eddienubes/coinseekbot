from sqlalchemy import TIMESTAMP, func
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, mapped_column


class Base(DeclarativeBase, MappedAsDataclass):
    created_at = mapped_column(TIMESTAMP, init=False, server_default=func.now(), nullable=False)
    updated_at = mapped_column(TIMESTAMP, init=False, server_default=func.now(), onupdate=func.now(), nullable=False)
