import sqlalchemy as sa
from numpy import save
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import InstrumentedAttribute

from crypto.entities.crypto_watch import CryptoWatch
from postgres import PgRepo, pg_session


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
