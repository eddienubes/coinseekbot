from typing import Mapping, cast, TypeVar

from sqlalchemy.dialects.postgresql import Insert
from sqlalchemy.orm import MappedColumn, InstrumentedAttribute

from .base import Base
from .pg_session import pg_session_ctx
from .repo import Repo


class PgRepo(Repo):
    T = TypeVar('T', bound=Base)

    def __init__(self):
        super().__init__(pg_session_ctx)

    def on_conflict_do_update_mapping(self,
                                      entity: T,
                                      insert: Insert,
                                      conflict: MappedColumn | InstrumentedAttribute) -> Mapping:

        hm = dict()

        primary_columns = [col.name for col in entity.__table__.primary_key.columns]
        foreign_keys = [col.name for col in entity.__table__.foreign_keys]

        for key in insert.excluded.keys():
            col: MappedColumn = insert.excluded[key]

            if col.name != conflict.name and col.name not in primary_columns and col.name not in foreign_keys:
                hm[key] = getattr(insert.excluded, key)

        return hm
