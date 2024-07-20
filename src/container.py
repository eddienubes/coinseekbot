import logging
from typing import TypeVar, Type

from bot.bot_inline_query_router import BotInlineQueryRouter
from bot.bot_personal_commands_router import BotPersonalCommandsRouter
from exchanges.binance import BinanceAssetsQueryApi
from bot.telegram_bot import TelegramBot
from exchanges.binance.binance_assets_query_service import BinanceAssetsQueryService
from exchanges.binance.binance_crypto_asset_repo import BinanceCryptoAssetRepo
from postgres.postgres_repo import PostgresRepo
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
        tg_bot = TelegramBot()

        bot_personal_commands_handler = BotPersonalCommandsRouter()

        redis_service = RedisService()

        assets_query_api = BinanceAssetsQueryApi()
        binance_assets_service = BinanceAssetsQueryService(assets_query_api, redis_service)

        bot_inline_query_handler = BotInlineQueryRouter(binance_assets_service)

        postgres_repo = PostgresRepo()
        binance_crypto_asset_repo = BinanceCryptoAssetRepo()

        instances = [
            tg_bot,
            assets_query_api,
            bot_inline_query_handler,
            bot_personal_commands_handler,
            binance_assets_service,
            redis_service,
            postgres_repo,
            binance_crypto_asset_repo
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
