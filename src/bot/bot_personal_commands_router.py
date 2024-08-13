from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.telegram_bot import TelegramBot
from exchanges.binance import BinanceAssetsQueryApi


@TelegramBot.router()
class BotPersonalCommandsRouter:
    def __init__(self):
        self.assets_query_api = BinanceAssetsQueryApi()

    @TelegramBot.handle_message(CommandStart())
    async def start(self, message: Message):
        await message.reply(
            "Hello! I'm a bot that can help you with your assets. Use /help to see all available commands.")
