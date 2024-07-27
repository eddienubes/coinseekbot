from typing import Mapping, cast

from sqlalchemy.dialects.postgresql import Insert
from sqlalchemy.orm import MappedColumn, InstrumentedAttribute

from .pg_session import pg_session_ctx
from .repo import Repo


class PgRepo(Repo):
    def __init__(self):
        super().__init__(pg_session_ctx)

    def on_conflict_do_update_mapping(self, insert: Insert,
                                      conflict: MappedColumn) -> Mapping:

        hm = dict()

        for key in insert.excluded.keys():
            col: MappedColumn = insert.excluded[key]

            if col.name != conflict.name:
                hm[key] = getattr(insert.excluded, key)

        return hm
