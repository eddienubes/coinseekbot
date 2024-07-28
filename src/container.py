import logging
from typing import TypeVar, Type

from bot.bot_inline_query_router import BotInlineQueryRouter
from bot.bot_personal_commands_router import BotPersonalCommandsRouter
from cron import CronService
from crypto.crypto_assets_repo import CryptoAssetsRepo
from crypto.crypto_ingest_service import CryptoIngestService
from exchanges.binance import (BinanceAssetsQueryApi,
                               BinanceAssetsQueryService,
                               BinanceCronService,
                               BinanceCryptoAssetRepo,
                               BinanceCryptoTradingPairsRepo,
                               BinanceS3Service, BinanceIngestService, BinanceTradingPairsService
                               )
from bot.telegram_bot import TelegramBot
from exchanges.binance.clients.binance_ui_api import BinanceUiApi
from postgres.alembic.entities import register_entities
from postgres.postgres_service import PostgresService
from redis_client import RedisService
from utils.singleton import Singleton


class Container(metaclass=Singleton):
    """Singleton IoC container"""
    __T = TypeVar('__T')

    # Run all async initializers
    def __init__(self):
        self.container = dict()
        self.__initialized = False

    def get(self, cls: Type[__T]) -> __T:
        if not self.__initialized:
            raise ValueError("Container is not initialized")

        instance = self.container.get(cls)
        if not instance:
            raise ValueError(f"Instance of {cls} not found in container")
        return instance

    async def init(self):
        register_entities()

        tg_bot = TelegramBot()

        bot_personal_commands_handler = BotPersonalCommandsRouter()

        redis_service = RedisService()

        assets_query_api = BinanceAssetsQueryApi()

        postgres_service = PostgresService()
        cron_service = CronService()

        binance_crypto_asset_repo = BinanceCryptoAssetRepo()
        binance_crypto_trading_pairs_repo = BinanceCryptoTradingPairsRepo()
        binance_s3_service = BinanceS3Service()
        binance_ingest_service = BinanceIngestService(
            assets_query_api,
            binance_crypto_asset_repo,
            binance_crypto_trading_pairs_repo,
            binance_s3_service
        )
        binance_trading_pairs_service = BinanceTradingPairsService(
            redis_service=redis_service,
            trading_pairs_repo=binance_crypto_trading_pairs_repo,
            assets_query_api=assets_query_api
        )

        binance_cron_service = BinanceCronService(
            binance_ingest_service,
            cron_service,
            trading_pairs_service=binance_trading_pairs_service
        )
        binance_ui_api = BinanceUiApi()

        binance_assets_service = BinanceAssetsQueryService(redis_service=redis_service,
                                                           binance_ui_api=binance_ui_api)

        crypto_asset_repo = CryptoAssetsRepo()
        crypto_ingest_service = CryptoIngestService(
            crypto_repo=crypto_asset_repo,
            binance_ui_api=binance_ui_api,
            cron=cron_service,
            redis=redis_service
        )
        bot_inline_query_handler = BotInlineQueryRouter(binance_assets_service)

        instances = [
            crypto_asset_repo,
            crypto_ingest_service,
            tg_bot,
            assets_query_api,
            bot_inline_query_handler,
            bot_personal_commands_handler,
            binance_assets_service,
            redis_service,
            postgres_service,
            binance_crypto_asset_repo,
            binance_cron_service,
            binance_s3_service,
            cron_service,
            binance_crypto_trading_pairs_repo,
            binance_trading_pairs_service,
            binance_ingest_service,
            binance_ui_api,
        ]

        for instance in instances:
            classname: str = type(instance).__name__
            logging.info(f"Initializing {classname}...")
            self.container[type(instance)] = instance

            on_module_init = getattr(instance, "on_module_init", None)
            if callable(on_module_init):
                await on_module_init()

        self.__initialized = True

    async def destroy(self):
        for instance in self.container.values():
            on_module_destroy = getattr(instance, "on_module_destroy", None)
            if callable(on_module_destroy):
                await on_module_destroy()
        self.container.clear()
        self.__initialized = False
