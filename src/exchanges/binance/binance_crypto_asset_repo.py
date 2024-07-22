from sqlalchemy import select

from .entities.binance_crypto_asset import BinanceCryptoAsset
from postgres import PgRepo, pg_session
from utils import faker

print("crypto asset repo")


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
    async def get_non_existent_tickers(self, tickers: list[str]) -> list[str]:
        query = select(BinanceCryptoAsset).where(BinanceCryptoAsset.ticker.in_(tickers))

        hits_raw = await self.session.execute(query)
        hits = [asset.ticker for asset in hits_raw.scalars().all()]

        return list(filter(lambda ticker: ticker not in hits, tickers))

    @pg_session
    async def insert(self, asset: BinanceCryptoAsset) -> BinanceCryptoAsset:
        return await self._insert(entity=BinanceCryptoAsset, value=asset)

    @pg_session
    async def insert_many(self, assets: list[BinanceCryptoAsset]) -> list[BinanceCryptoAsset]:
        return await self._insert_many(entity=BinanceCryptoAsset, values=assets)
