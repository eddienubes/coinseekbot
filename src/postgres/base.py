from datetime import datetime

from sqlalchemy import TIMESTAMP, func
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now(),
                                                 nullable=False)

    def to_dict(self, **kwargs) -> dict:
        """
        Convert SQLAlchemy model to an insertable dict.
        Strips everything (relations, extra attributes etc.) besides regular table columns
        :param kwargs: Additional fields to add or override
        """
        hm = dict()

        # primary_columns = [col.name for col in self.__table__.primary_key.columns]
        # foreign_keys = [col.name for col in self.__table__.foreign_keys]

        # noinspection PyTypeChecker
        regular_columns = [col.name for col in self.__table__.columns]

        for k, v in vars(self).items():
            if k in regular_columns:
                hm[k] = v

        return {
            **hm,
            **kwargs
        }

    def __repr__(self):
        return f'{self.__class__.__name__}({self.to_dict()})'
