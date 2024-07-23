from typing import Iterable

from sqlalchemy import select

from .entities.binance_crypto_asset import BinanceCryptoAsset
from postgres import PgRepo, pg_session
from utils import faker
from .types.ticker_existence_filter import TickerExistenceFilter


class BinanceCryptoAssetRepo(PgRepo):
    @pg_session
    async def generate(self) -> BinanceCryptoAsset:
        asset = BinanceCryptoAsset(
            name=faker.pystr(3, 10),
            ticker=faker.pystr(3, 10),
            logo_s3_key=faker.image_url()
        )
        await self.add(asset)

        return asset

    @pg_session
    async def search_by_tickers(self, tickers: Iterable[str]) -> TickerExistenceFilter:
        query = select(BinanceCryptoAsset).where(BinanceCryptoAsset.ticker.in_(tickers))

        hits_raw = await self.session.execute(query)
        hits_hm = {hit.ticker: hit for hit in hits_raw.scalars().all()}

        result = TickerExistenceFilter(
            hits=[],
            misses=[]
        )

        for ticker in tickers:
            if ticker in hits_hm:
                result.hits.append(hits_hm[ticker])
            else:
                result.misses.append(ticker)

        return result

    @pg_session
    async def insert(self, asset: BinanceCryptoAsset) -> BinanceCryptoAsset:
        return await self._insert(entity=BinanceCryptoAsset, value=asset)

    @pg_session
    async def insert_many(self, assets: list[BinanceCryptoAsset]) -> list[BinanceCryptoAsset]:
        return await self._insert_many(entity=BinanceCryptoAsset, values=assets)

    @pg_session
    async def delete_all(self) -> None:
        await self._delete_all(entity=BinanceCryptoAsset)
