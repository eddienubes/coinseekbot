from bot.bot_inline_query_router import BotInlineQueryRouter
from bot.bot_personal_commands_router import BotPersonalCommandsRouter
from exchanges.binance import BinanceAssetsQueryApi
from bot.telegram_bot import TelegramBot

tg_bot = TelegramBot()
assets_query_api = BinanceAssetsQueryApi()
bot_inline_query_handler = BotInlineQueryRouter()
bot_personal_commands_handler = BotPersonalCommandsRouter()

instances = [
    tg_bot,
    assets_query_api,
    bot_inline_query_handler,
    bot_personal_commands_handler
]


# Run all async initializers
async def init():
    for instance in instances:
        on_module_init = getattr(instance, "on_module_init", None)
        if callable(on_module_init):
            await on_module_init()
