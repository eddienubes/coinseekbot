import logging
from typing import TypeVar, Type

from bot.bot_inline_query_router import BotInlineQueryRouter
from bot.bot_personal_commands_router import BotPersonalCommandsRouter
from exchanges.binance import BinanceAssetsQueryApi
from bot.telegram_bot import TelegramBot
from exchanges.binance.binance_assets_query_service import BinanceAssetsQueryService
from redis_client import RedisService


class Container:
    __T = TypeVar('__T')

    # Run all async initializers
    def __init__(self):
        self.container = dict()

    def get(self, cls: Type[__T]) -> __T:
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

        instances = [
            tg_bot,
            assets_query_api,
            bot_inline_query_handler,
            bot_personal_commands_handler,
            binance_assets_service,
            redis_service
        ]

        for instance in instances:
            classname: str = type(instance).__name__
            logging.info(f"Initializing {classname}...")
            self.container[type(instance)] = instance

            on_module_init = getattr(instance, "on_module_init", None)
            if callable(on_module_init):
                await on_module_init()

    async def destroy(self):
        for instance in self.container.values():
            on_module_destroy = getattr(instance, "on_module_destroy", None)
            if callable(on_module_destroy):
                await on_module_destroy()
        self.container.clear()
