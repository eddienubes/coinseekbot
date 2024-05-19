import asyncio
import logging

from aiogram import Bot, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from dispatcher import dp

from config import Config


@dp.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


async def main():
    bot = Bot(token=Config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
