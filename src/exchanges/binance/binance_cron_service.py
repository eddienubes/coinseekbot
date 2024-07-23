import asyncio
import logging
import itertools

from aiogram.client.session import aiohttp
from apscheduler.triggers.calendarinterval import CalendarIntervalTrigger
from apscheduler.triggers.interval import IntervalTrigger

from config import config
from cron import CronService
from postgres import pg_session
from .binance_crypto_trading_pairs_repo import BinanceCryptoTradingPairsRepo
from .binance_assets_query_api import BinanceAssetsQueryApi
from .binance_crypto_asset_repo import BinanceCryptoAssetRepo
from .binance_s3_service import BinanceS3Service
from .dtos.binance_spot_exchange_info_symbol import BinanceSpotExchangeInfoSymbol
from .entities.binance_crypto_asset import BinanceCryptoAsset
from .entities.binance_crypto_trading_pair import BinanceCryptoTradingPair


class BinanceCronService:
    def __init__(self, binance_assets_query_api: BinanceAssetsQueryApi,
                 binance_crypto_assets_repo: BinanceCryptoAssetRepo,
                 binance_crypto_trading_pairs_repo: BinanceCryptoTradingPairsRepo,
                 binance_s3_service: BinanceS3Service,
                 cron_service: CronService
                 ):
        self.__binance_assets_query_api = binance_assets_query_api
        self.__binance_crypto_assets_repo = binance_crypto_assets_repo
        self.__binance_crypto_trading_pairs_repo = binance_crypto_trading_pairs_repo
        self.__binance_s3_service = binance_s3_service
        self.__cron_service = cron_service
        self.__logger = logging.getLogger(BinanceCronService.__name__)

    @pg_session
    async def ingest_assets(self) -> None:
        """Create available on binance assets"""
        assets = await self.__binance_assets_query_api.get_all_assets()

        hm = dict()
        entities_hm = dict()

        for asset in assets.data:
            if not asset.logoUrl or not asset.assetName or not asset.assetCode:
                continue

            hm[asset.assetCode] = asset
            entities_hm[asset.assetCode] = BinanceCryptoAsset(
                name=asset.assetName,
                ticker=asset.assetCode
            )

        # Basically, truncate the table.
        # Perhaps, we could mark the records as deleted instead of deleting them.
        # But for now, let's just delete them.
        await self.__binance_crypto_assets_repo.delete_all()

        async with aiohttp.ClientSession() as session:
            async with asyncio.TaskGroup() as tg:
                for asset in entities_hm.values():
                    self.__logger.debug(f'Creating a record for ticker: {asset.ticker}')

                    logo_url = hm[asset.ticker].logoUrl

                    # Skip empty URLs
                    if not logo_url:
                        continue

                    async def upload(asset, logo_url):
                        self.__logger.debug(f'Uploading logo for ticker: {asset.ticker} with logo url: {logo_url}')
                        try:
                            async with session.get(logo_url) as res:
                                s3_key = await self.__binance_s3_service.upload_asset_logo(res.content, asset.ticker)

                            entities_hm[asset.ticker].logo_s3_key = s3_key
                        except Exception as e:
                            self.__logger.warning(
                                f'Failed to create a record for ticker: {asset.ticker}, logo url: {logo_url}, error: {e}')

                    tg.create_task(upload(asset, logo_url))

        entities = [asset for asset in entities_hm.values() if asset.logo_s3_key]

        await self.__binance_crypto_assets_repo.insert_many(entities)

    @pg_session
    async def ingest_trading_pairs(self) -> None:
        """Create available on binance trading pairs"""
        pairs = await self.__binance_assets_query_api.get_all_pairs()

        unique_assets = set[str]()
        hm = dict[str, BinanceSpotExchangeInfoSymbol]()

        for symbol in pairs.symbols:
            if not symbol.baseAsset or not symbol.quoteAsset or not symbol.status:
                continue

            unique_assets.add(symbol.baseAsset.upper())
            unique_assets.add(symbol.quoteAsset.upper())

            hm[symbol.symbol.upper()] = symbol

        # Basically, truncate the table.
        # Perhaps, we could mark the records as deleted instead of deleting them.
        # But for now, let's just delete them.
        await self.__binance_crypto_trading_pairs_repo.delete_all()

        search = await self.__binance_crypto_assets_repo.search_by_tickers(unique_assets)
        search_hits_hm = {asset.ticker: asset for asset in search.hits}

        entities = list[BinanceCryptoTradingPair]()

        for symbol in hm.values():
            if symbol.baseAsset.upper() in search.misses or symbol.quoteAsset.upper() in search.misses:
                self.__logger.warning(
                    f'{self.ingest_trading_pairs.__name__}: Asset not found for symbol: {symbol.symbol}')
                continue

            base_asset = search_hits_hm[symbol.baseAsset.upper()]
            quote_asset = search_hits_hm[symbol.quoteAsset.upper()]

            entities.append(
                BinanceCryptoTradingPair(
                    base_asset_uuid=base_asset.uuid,
                    base_asset_name=base_asset.name,
                    quote_asset_uuid=quote_asset.uuid,
                    quote_asset_name=quote_asset.name,
                    symbol=symbol.symbol,
                    status=symbol.status,
                    iceberg_allowed=symbol.icebergAllowed,
                    oco_allowed=symbol.ocoAllowed,
                    oto_allowed=symbol.otoAllowed,
                    quote_order_qty_market_allowed=symbol.quoteOrderQtyMarketAllowed,
                    allow_trailing_stop=symbol.allowTrailingStop,
                    cancel_replace_allowed=symbol.cancelReplaceAllowed,
                    is_spot_trading_allowed=symbol.isSpotTradingAllowed,
                    is_margin_trading_allowed=symbol.isMarginTradingAllowed
                )
            )

        # Inserting in chunks of 1000
        chunks = itertools.batched(entities, 1000)

        for chunk in chunks:
            await self.__binance_crypto_trading_pairs_repo.insert_many(chunk)

    @pg_session
    async def update_binance(self):
        await self.ingest_assets()
        await self.ingest_trading_pairs

    async def on_module_init(self):
        if config.env == 'test':
            return

        # Update assets every day at 01:00
        self.__cron_service.add_job(self.ingest_assets, CalendarIntervalTrigger(hour=1))
