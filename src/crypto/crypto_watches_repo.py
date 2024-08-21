import uuid

import sqlalchemy as sa
from numpy import save
from sqlalchemy import select, distinct
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import InstrumentedAttribute, aliased, contains_eager

from crypto.entities.crypto_asset import CryptoAsset
from crypto.entities.crypto_favourite import CryptoFavourite
from crypto.entities.crypto_watch import CryptoWatch, CryptoWatchStatus, WatchInterval
from postgres import PgRepo, pg_session
from telegram.entities.tg_chat import TgChat
from utils import Pageable
from typing import Sequence

type Watchlist = Pageable[tuple[CryptoWatch | None, CryptoAsset, CryptoFavourite | None]]


class CryptoWatchesRepo(PgRepo):
    @pg_session
    async def update(self, watch: CryptoWatch, by: list[sa.Column | InstrumentedAttribute]) -> None:
        await self._update(CryptoWatch, by, watch)

    @pg_session
    async def get_with_joins_by_chat(
            self,
            tg_chat_uuid: sa.UUID | str,
            asset_uuids_not_in: list[sa.UUID | str] = None,
            limit: int = 5,
            offset: int = 0
    ) -> Pageable[CryptoWatch]:
        query = (
            select(
                CryptoWatch
            )
            .join(CryptoWatch.asset)
            .join(CryptoWatch.tg_chat)
            .where(
                sa.and_(
                    tg_chat_uuid == CryptoWatch.tg_chat_uuid
                )
            )
            .order_by(
                CryptoWatch.status.desc(),
                CryptoWatch.updated_at.desc()
            )
            .limit(limit)
            .offset(offset)
            .options(
                contains_eager(CryptoWatch.asset),
                contains_eager(CryptoWatch.tg_chat)
            )
        )

        count_query = (
            sa.select(sa.func.count(CryptoWatch.uuid))
            .join(CryptoWatch.asset)
            .join(CryptoWatch.tg_chat)
            .where(
                sa.and_(
                    tg_chat_uuid == CryptoWatch.tg_chat_uuid
                )
            )
        )

        if asset_uuids_not_in:
            query = query.where(CryptoWatch.asset_uuid.notin_(asset_uuids_not_in))
            count_query = count_query.where(CryptoWatch.asset_uuid.notin_(asset_uuids_not_in))

        hits = await self.session.scalars(query)
        total = await self.session.scalar(count_query)

        return Pageable(
            hits=list(hits.all()),
            total=total,
            limit=limit,
            offset=offset
        )

    @pg_session
    async def upsert(self, watch: CryptoWatch) -> CryptoWatch:
        watch_dict = watch.to_dict()

        query = insert(CryptoWatch).values(watch_dict)
        query = query.on_conflict_do_update(
            index_elements=[CryptoWatch.asset_uuid, CryptoWatch.tg_chat_uuid],
            set_=self.on_conflict_do_update_mapping(
                entity=CryptoWatch,
                insert=query,
                conflict=[CryptoWatch.asset_uuid, CryptoWatch.tg_chat_uuid],
                update=list(watch_dict.keys())
            )
        ).returning(CryptoWatch)

        raw_hit = await self.session.scalar(query)

        return raw_hit

    @pg_session
    async def bulk_upsert(self, watches: list[CryptoWatch]) -> list[CryptoWatch]:
        if not watches:
            return []

        watches_dicts = [watch.to_dict() for watch in watches]

        query = insert(CryptoWatch).values(watches_dicts)
        query = query.on_conflict_do_update(
            index_elements=[CryptoWatch.asset_uuid, CryptoWatch.tg_chat_uuid],
            set_=self.on_conflict_do_update_mapping(
                entity=CryptoWatch,
                insert=query,
                conflict=[CryptoWatch.asset_uuid, CryptoWatch.tg_chat_uuid],
                update=list(watches_dicts[0].keys())
            )
        ).returning(CryptoWatch)

        raw_hits = await self.session.scalars(query)

        return list(raw_hits.all())

    @pg_session
    async def get_watchlist(
            self,
            tg_user_uuid: sa.UUID | str,
            tg_chat_uuid: sa.UUID | str,
            limit: int = 5,
            offset: int = 0
    ) -> Watchlist:
        query = (
            select(CryptoWatch, CryptoAsset, CryptoFavourite)
            .outerjoin_from(
                CryptoWatch, CryptoFavourite,
                sa.and_(
                    CryptoFavourite.asset_uuid == CryptoWatch.asset_uuid,
                    CryptoFavourite.tg_user_uuid == tg_user_uuid
                ), full=True
            )
            .join_from(
                CryptoWatch, CryptoAsset,
                sa.or_(
                    CryptoAsset.uuid == CryptoWatch.asset_uuid,
                    CryptoAsset.uuid == CryptoFavourite.asset_uuid
                )
            )
            .where(
                sa.or_(
                    CryptoWatch.uuid.is_(None),
                    sa.and_(
                        CryptoWatch.uuid.is_not(None),
                        CryptoWatch.tg_chat_uuid == tg_chat_uuid
                    )
                )
            )
            .order_by(
                CryptoWatch.status,
                CryptoFavourite.updated_at.nullslast(),
                CryptoWatch.updated_at.nullslast(),
            )
            .limit(limit)
            .offset(offset)

        )

        count_query = (
            select(sa.func.count())
            .outerjoin_from(
                CryptoWatch, CryptoFavourite,
                sa.and_(
                    CryptoFavourite.asset_uuid == CryptoWatch.asset_uuid,
                    CryptoFavourite.tg_user_uuid == tg_user_uuid
                ), full=True
            )
            .join_from(
                CryptoWatch, CryptoAsset,
                sa.or_(
                    CryptoAsset.uuid == CryptoWatch.asset_uuid,
                    CryptoAsset.uuid == CryptoFavourite.asset_uuid
                )
            )
            .where(
                sa.or_(
                    CryptoWatch.uuid.is_(None),
                    sa.and_(
                        CryptoWatch.uuid.is_not(None),
                        CryptoWatch.tg_chat_uuid == tg_chat_uuid
                    )
                )
            )
        )

        hits = await self.session.execute(query)
        total = await self.session.scalar(count_query)

        return Pageable(
            hits=list(hits.all()),
            total=total,
            limit=limit,
            offset=offset
        )

    @pg_session
    async def get_watches_to_notify(self) -> list[CryptoWatch]:
        """
        Finds watches that are due for execution.
        In order for a watch to be considered due, at least one of the watches per interval in the group (tg_chat) must be due.
        This is done in order to notify the same intervals at the same time and avoid spamming the user.
        """

        watch_alias = aliased(CryptoWatch)

        subquery = aliased(
            select(CryptoWatch)
            .distinct(sa.tuple_(CryptoWatch.tg_chat_uuid, CryptoWatch.interval))
            .where(
                sa.or_(
                    # Execution is due
                    CryptoWatch.next_execution_at <= sa.func.now(),
                    # Haven't been executed yet
                    CryptoWatch.next_execution_at.is_(None)
                )
            )
            .subquery()
        )

        query = (
            select(watch_alias)
            .join(watch_alias.asset)
            .join(watch_alias.tg_chat)
            .join(CryptoAsset.latest_quote)
            .outerjoin(
                subquery,
                sa.and_(
                    subquery.c.tg_chat_uuid == watch_alias.tg_chat_uuid,
                    subquery.c.status == CryptoWatchStatus.ACTIVE,
                    subquery.c.interval == watch_alias.interval
                )
            )
            .where(
                sa.and_(
                    watch_alias.status == CryptoWatchStatus.ACTIVE,
                    subquery.c.uuid.is_not(None),
                )
            )
            .options(
                contains_eager(watch_alias.asset)
                .contains_eager(CryptoAsset.latest_quote),
                contains_eager(watch_alias.tg_chat),
            )
        )

        raw_hits = await self.session.scalars(query)

        return list(raw_hits.all())
