import asyncio
import logging

from aiogram.client.session import aiohttp
from apscheduler.triggers.interval import IntervalTrigger

from cron import CronService
from postgres import pg_session
from .binance_assets_query_api import BinanceAssetsQueryApi
from .binance_crypto_asset_repo import BinanceCryptoAssetRepo
from .binance_s3_service import BinanceS3Service
from .entities.binance_crypto_asset import BinanceCryptoAsset
from apscheduler import AsyncScheduler
from apscheduler.triggers.cron import CronTrigger


class BinanceCronService:
    def __init__(self, binance_assets_query_api: BinanceAssetsQueryApi,
                 binance_crypto_assets_repo: BinanceCryptoAssetRepo,
                 binance_s3_service: BinanceS3Service,
                 cron_service: CronService
                 ):
        self.__binance_assets_query_api = binance_assets_query_api
        self.__binance_crypto_assets_repo = binance_crypto_assets_repo
        self.__binance_s3_service = binance_s3_service
        self.__cron_service = cron_service
        self.__logger = logging.getLogger(BinanceCronService.__name__)

    @pg_session
    async def ingest_assets(self) -> None:
        """Create available on binance assets
        TODO: Perhaps, we should literally truncate the entire table and re-ingest all assets
        """
        assets = await self.__binance_assets_query_api.get_all_assets()

        hm = dict()

        for asset in assets.data:
            if not asset.logoUrl or not asset.assetName or not asset.assetCode:
                continue

            hm[asset.assetCode] = asset

        non_existing_tickers = await self.__binance_crypto_assets_repo.get_non_existent_tickers(list(hm.keys()))

        non_existing_hm = {ticker: BinanceCryptoAsset(
            name=hm[ticker].assetName,
            ticker=ticker
        ) for ticker in non_existing_tickers}

        async with aiohttp.ClientSession() as session:
            async with asyncio.TaskGroup() as tg:
                for asset in non_existing_hm.values():
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
                                non_existing_hm[asset.ticker].logo_s3_key = s3_key

                            non_existing_hm[asset.ticker].logo_s3_key = s3_key
                        except Exception as e:
                            self.__logger.warning(
                                f'Failed to create a record for ticker: {asset.ticker}, logo url: {logo_url}, error: {e}')

                    tg.create_task(upload(asset, logo_url))

        entities = [asset for asset in non_existing_hm.values() if asset.logo_s3_key]

        await self.__binance_crypto_assets_repo.insert_many(entities)

    async def on_module_init(self):
        # Update assets every 12 hours
        self.__cron_service.add_job(self.ingest_assets, IntervalTrigger(hours=12))
