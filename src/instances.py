from exchanges.binance import BinanceAssetsQueryApi
from bot.bot_inline_query_service import BotInlineQueryService
from bot.bot_personal_commands_service import BotPersonalCommandsService
from bot.telegram_bot import TelegramBot

bot = TelegramBot()
assets_query_api = BinanceAssetsQueryApi()
bot_inline_query_service = BotInlineQueryService(assets_query_api)
bot_personal_commands_service = BotPersonalCommandsService()
