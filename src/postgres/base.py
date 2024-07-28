from datetime import datetime

from sqlalchemy import TIMESTAMP, func
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy.orm.collections import InstrumentedList


class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now(),
                                                 nullable=False)

    def to_dict(self, **kwargs) -> dict:
        """Convert SQLAlchemy model to dict
        :param kwargs: Additional fields to add or override
        """
        hm = dict()

        for k, v in vars(self).items():
            if (not k.startswith('_')  # Filter out private fields
                    and not callable(v)  # Filter out methods
                    and not isinstance(v, Base)
                    and not isinstance(v, InstrumentedList)  # Filter out joined relationships
            ):
                hm[k] = v

        return {
            **hm,
            **kwargs
        }

    def __repr__(self):
        return f'{self.__class__.__name__}({self.to_dict()})'
