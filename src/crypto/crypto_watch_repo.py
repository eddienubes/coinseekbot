import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.orm import aliased

from crypto.entities.crypto_asset import CryptoAsset
from crypto.entities.crypto_watch import CryptoWatch
from postgres import PgRepo, pg_session
from telegram.tg_chat import TgChat


class CryptoWatchRepo(PgRepo):
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
