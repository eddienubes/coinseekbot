from datetime import datetime

from sqlalchemy import TIMESTAMP, func, Column
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

import json


class Encoder(json.JSONEncoder):
    """Custom JSON encoder that converts objects to strings"""

    def default(self, o):
        try:
            return json.JSONEncoder.default(self, o)
        except Exception as e:
            return str(o)


class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(),
                                                 onupdate=func.now(),
                                                 nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    __cols: dict[str, Column] | None = None

    @classmethod
    def get_cols_map(cls) -> dict[str, Column]:
        """Get a map of column names to column objects"""

        if cls.__cols:
            return cls.__cols

        cols = cls.__table__.columns
        hm = dict()

        # noinspection PyTypeChecker
        for col in cols:
            hm[col.name] = col

        cls.__cols = hm

        return cls.__cols

    def to_dict(self, **kwargs) -> dict:
        """
        Convert SQLAlchemy model to an insertable dict.
        Strips everything (relations, extra attributes etc.) besides regular table columns
        :param kwargs: Additional fields to add or override
        """
        hm = dict()
        cols = self.__class__.get_cols_map()

        for k, v in vars(self).items():
            if k not in cols:
                continue

            col = cols[k]

            # Strips nones if column is not nullable and has a default value
            if v is None and not col.nullable and (col.default or col.server_default):
                continue

            hm[k] = v

        return {
            **hm,
            **kwargs
        }

    def __hash__(self) -> int:
        this_dict = self.to_dict()
        # Sort the dict by key to make sure the hash is consistent
        this_dict = dict(sorted(this_dict.items(), key=lambda x: x[0]))
        json_str = json.dumps(this_dict, cls=Encoder)

        return hash(json_str)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.to_dict()})'
