from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import Config


class TelegramBot:
    dp = Dispatcher()

    async def start(self) -> None:
        bot = Bot(token=Config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        await TelegramBot.dp.start_polling(bot)
