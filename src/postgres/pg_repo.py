from typing import Mapping

from sqlalchemy.dialects.postgresql import Insert
from sqlalchemy.orm import MappedColumn, InstrumentedAttribute

from .pg_session import pg_session_ctx
from .repo import Repo


class PgRepo(Repo):
    def __init__(self):
        super().__init__(pg_session_ctx)

    def on_conflict_do_update_mapping(self, insert: Insert,
                                      conflict: MappedColumn) -> Mapping:
        return {k: getattr(insert.excluded, k) for k in insert.excluded.keys() if k != conflict.name}
