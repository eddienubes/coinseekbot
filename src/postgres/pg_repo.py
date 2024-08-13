import logging
from typing import Mapping, cast, TypeVar, Sequence

from sqlalchemy import Column, inspect
from sqlalchemy.dialects.postgresql import Insert
from sqlalchemy.orm import MappedColumn, InstrumentedAttribute
import sqlalchemy as sa

from . import pg_engine
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
                                          MappedColumn | InstrumentedAttribute],
                                      update: Sequence[str] = None
                                      ) -> Mapping:

        """TODO: Use set of keys to update only columns provided in values clause"""
        hm = dict()

        if isinstance(conflict, Sequence):
            conflict_names = {conflict.name for conflict in conflict}
        else:
            conflict_names = {conflict.name}

        # If the explicit update list provided
        if update:
            for col_name in update:
                if col_name in conflict_names:
                    continue

                # noinspection PyTypeChecker
                excluded = getattr(insert.excluded, col_name, None)

                if excluded is None:
                    raise ValueError(f'Column {col_name} is not present in the excluded clause.')

                hm[col_name] = excluded

            return hm

        regular_cols = entity.get_cols_map()

        for key in regular_cols:
            col_name: Column = regular_cols[key]

            # Skip primary keys and columns that are in the conflict list
            if col_name.name not in conflict_names and col_name.primary_key is False:
                hm[key] = getattr(insert.excluded, key)

        return hm
