import sqlalchemy as sa
from numpy import save
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import InstrumentedAttribute, aliased, contains_eager

from crypto.entities.crypto_asset import CryptoAsset
from crypto.entities.crypto_watch import CryptoWatch, CryptoWatchStatus
from postgres import PgRepo, pg_session
from telegram.entities.tg_chat import TgChat


class CryptoWatchesRepo(PgRepo):
    @pg_session
    async def update(self, watch: CryptoWatch, by: list[sa.Column | InstrumentedAttribute]) -> None:
        await self._update(CryptoWatch, by, watch)

    @pg_session
    async def get_with_joins(self, asset_uuid: sa.UUID, tg_chat_uuid: sa.UUID) -> CryptoWatch | None:
        query = (
            select(
                CryptoWatch
            )
            .join(CryptoWatch.asset)
            .join(CryptoWatch.tg_chat)
            .where(
                sa.and_(
                    asset_uuid == CryptoWatch.asset_uuid,
                    tg_chat_uuid == CryptoWatch.tg_chat_uuid
                )
            ).options(
                contains_eager(CryptoWatch.asset),
                contains_eager(CryptoWatch.tg_chat)
            )
        )

        raw_hit = await self.session.scalar(query)

        return raw_hit

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
    async def get_watches_to_notify(self) -> list[CryptoWatch]:
        query = (
            select(CryptoWatch)
            .join(CryptoWatch.asset)
            .join(CryptoWatch.tg_chat)
            .join(CryptoAsset.latest_quote)
            .where(
                sa.and_(
                    CryptoWatch.status == CryptoWatchStatus.ACTIVE,
                    sa.or_(
                        # Execution is due
                        CryptoWatch.next_execution_at <= sa.func.now(),
                        # Haven't been executed yet
                        CryptoWatch.next_execution_at.is_(None)
                    ),
                    CryptoWatch.tg_chat.and_(
                        TgChat.is_removed.is_(False),
                    )
                )
            )
            .options(
                contains_eager(CryptoWatch.asset)
                .contains_eager(CryptoAsset.latest_quote),
                contains_eager(CryptoWatch.tg_chat),
            )
        )

        raw_hits = await self.session.scalars(query)

        return list(raw_hits.all())
