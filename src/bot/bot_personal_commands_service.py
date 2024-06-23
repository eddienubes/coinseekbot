from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.telegram_bot import TelegramBot


class BotPersonalCommandsService:
    def __int__(self):
        pass

    @TelegramBot.dp.message(CommandStart())
    async def start(self, message: Message):
        await message.reply(
            "Hello! I'm a bot that can help you with your assets. Use /help to see all available commands.")
