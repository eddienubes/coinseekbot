import logging
from typing import Mapping, cast, TypeVar, Sequence

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import Insert
from sqlalchemy.orm import MappedColumn, InstrumentedAttribute
import sqlalchemy as sa

from .base import Base
from .pg_session import pg_session_ctx
from .repo import Repo


class PgRepo(Repo):
    T = TypeVar('T', bound=Base)

    def __init__(self):
        super().__init__(pg_session_ctx)

        self._logger = logging.getLogger(self.__class__.__name__)

    def on_conflict_do_update_mapping(self,
                                      entity: T,
                                      insert: Insert,
                                      conflict: MappedColumn | InstrumentedAttribute | Sequence[
                                          MappedColumn | InstrumentedAttribute]
                                      ) -> Mapping:

        """TODO: Use set of keys to update only columns provided in values clause"""
        hm = dict()

        if isinstance(conflict, Sequence):
            conflict_names = {conflict.name for conflict in conflict}
        else:
            conflict_names = {conflict.name}

        regular_cols = entity.get_cols_map()

        print(insert.excluded)

        for key in regular_cols:
            col: Column = regular_cols[key]

            if (col.name
                    # Drop columns that are in conflict columns
                    not in conflict_names
                    # Drop columns that are not in regular columns (relations, pks etc.)
                    # and not col.nullable
            ):
                # n = 
                hm[key] = sa.text(f'coalesce(excluded.{col.name}, {col.name})')

        return hm
