from typing import cast

from sqlalchemy.orm import MappedColumn, InstrumentedAttribute

from crypto.entities.crypto_asset import CryptoAsset
from postgres import PgRepo, pg_session

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert


class CryptoAssetRepo(PgRepo):

    @pg_session
    async def generate(self) -> CryptoAsset:
        asset = CryptoAsset.random()
        await self.add(asset)
        return asset

    @pg_session
    async def find_by_ticker(self, ticker: str) -> CryptoAsset | None:
        query = select(CryptoAsset).where(ticker == CryptoAsset.ticker)

        hit = await self.session.execute(query)
        return hit.scalar()

    @pg_session
    async def bulk_insert(self, assets: list[CryptoAsset]) -> list[CryptoAsset]:
        return await self._insert_many(entity=CryptoAsset, values=assets)

    @pg_session
    async def bulk_upsert(self, assets: list[CryptoAsset],
                          conflict: MappedColumn | InstrumentedAttribute = CryptoAsset.uuid
                          ) -> list[CryptoAsset]:
        stmt = insert(CryptoAsset).values(
            [asset.to_dict() for asset in assets]
        )

        stmt = stmt.on_conflict_do_update(
            index_elements=[conflict],
            set_=self.on_conflict_do_update_mapping(stmt, conflict)
        ).returning(CryptoAsset)

        hits_raw = await self.session.execute(stmt)

        return cast(list[CryptoAsset], list(hits_raw.scalars().all()))
