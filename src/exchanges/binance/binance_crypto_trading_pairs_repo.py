from sqlalchemy import UUID, select

from exchanges.binance.entities import BinanceCryptoTradingPair
from postgres import PgRepo, pg_session


class BinanceCryptoTradingPairsRepo(PgRepo):
    @pg_session
    async def generate(self, base_asset_uuid: UUID, quote_asset_uuid: UUID) -> BinanceCryptoTradingPair:
        """UoW-enabled"""

        pair = BinanceCryptoTradingPair.random(base_asset_uuid, quote_asset_uuid)

        await self.add(pair)

        return pair

    # @pg_session
    # async def search_by_tickers(self, tickers: Iterable[str]) -> TickerExistenceFilter:
    #     query = select(BinanceCryptoAsset).where(BinanceCryptoAsset.ticker.in_(tickers))
    # 
    #     hits_raw = await self.session.execute(query)
    #     hits_hm = {hit.ticker: hit for hit in hits_raw.scalars().all()}
    # 
    #     result = TickerExistenceFilter(
    #         hits=[],
    #         misses=[]
    #     )
    # 
    #     for ticker in tickers:
    #         if ticker in hits_hm:
    #             result.hits.append(hits_hm[ticker])
    #         else:
    #             result.misses.append(ticker)
    # 
    #     return result

    @pg_session
    async def insert(self, pair: BinanceCryptoTradingPair) -> BinanceCryptoTradingPair:
        return await self._insert(entity=BinanceCryptoTradingPair, value=pair)

    @pg_session
    async def insert_many(self, assets: list[BinanceCryptoTradingPair]) -> list[BinanceCryptoTradingPair]:
        return await self._insert_many(entity=BinanceCryptoTradingPair, values=assets)

    @pg_session
    async def delete_all(self) -> None:
        await self._delete_all(entity=BinanceCryptoTradingPair)

    @pg_session
    async def get_all(self) -> list[BinanceCryptoTradingPair]:
        hits_raw = await self.session.execute(select(BinanceCryptoTradingPair))
        hits = hits_raw.scalars().all()

        return list(hits)
