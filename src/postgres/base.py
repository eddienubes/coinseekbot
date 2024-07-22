from datetime import datetime

from sqlalchemy import TIMESTAMP, func
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now(),
                                                 nullable=False)

    def to_dict(self, **kwargs) -> dict:
        """Convert SQLAlchemy model to dict
        :param kwargs: Additional fields to add or override
        """
        obj = {k: v for k, v in vars(self).items() if not k.startswith('_')}

        return {
            **obj,
            **kwargs
        }

    def __repr__(self):
        return f'{self.__class__.__name__}({self.to_dict()})'
