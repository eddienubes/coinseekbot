import asyncio
import json
import logging

from config import config
from .binance_crypto_trading_pairs_repo import BinanceCryptoTradingPairsRepo
from .clients.binance_assets_query_api import BinanceAssetsQueryApi
from .dtos.binance_symbol_24h_change_dto import BinanceSymbol24hChangeDto
from .types.binance_trading_pair_price_change_search import BinanceTradingPairPriceChangeSearch
from redis_client import RedisService


class BinanceTradingPairsService:
    def __init__(self,
                 redis_service: RedisService,
                 trading_pairs_repo: BinanceCryptoTradingPairsRepo,
                 assets_query_api: BinanceAssetsQueryApi
                 ):
        self.__redis_service = redis_service
        self.__trading_pairs_repo = trading_pairs_repo
        self.__assets_query_api = assets_query_api
        self.__logger = logging.getLogger(self.__class__.__name__)

    async def update_trading_pair_price_changes(self):
        """Update trading pair prices in Redis"""
        # chunks = itertools.batched(symbols, 500)
        # 
        # prices = list[BinanceSymbol24hChangeDto]()
        # 
        # for chunk in chunks:
        #     hits = await self.__assets_query_api.get_24h_price_changes(list(chunk))
        #     # Throttle the requests a bit to avoid rate limiting
        #     await asyncio.sleep(0.5)
        #     prices.extend(hits)

        # Chunking by 100 actually consumers more weight than just sending all symbols at once
        prices = await self.__assets_query_api.get_24h_price_changes()

        price_hm = {self.__get_price_key(price.symbol.upper()): price.to_json() for price in prices}

        await self.__redis_service.mset(price_hm)

    async def get_trading_pair_price_change(self, symbol: str) -> BinanceSymbol24hChangeDto | None:
        """Get trading pair price change from Redis"""
        price = await self.__redis_service.get(symbol.upper())

        if not price:
            return None

        # TODO: I think there's a bug here. It doesn't create an actual dataclass instance.
        return json.loads(price)

    async def search_trading_pair_price_changes(self, symbols: list[str]) -> BinanceTradingPairPriceChangeSearch:
        """Search for multiple trading pair price changes from Redis"""
        misses = list[str]()
        hits = list[BinanceSymbol24hChangeDto]()

        # Let's purposefully not use mget here.
        async with asyncio.TaskGroup() as g:
            async def search(symbol: str):
                price = await self.get_trading_pair_price_change(symbol)

                if price:
                    hits.append(price)
                else:
                    misses.append(symbol)

            g.create_task(search(symbol) for symbol in symbols)

        return BinanceTradingPairPriceChangeSearch(hits=hits, misses=misses)

    def __get_price_key(self, postfix: str) -> str:
        return f'binance_trading_pair_prices:{postfix}'

    async def on_module_init(self):
        if config.env == 'test':
            return

        # await self.update_trading_pair_price_changes()
