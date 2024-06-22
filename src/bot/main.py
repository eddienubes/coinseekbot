import asyncio
import inspect
import logging
from random import random

from aiogram import Bot, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from dispatcher import dp

from config import Config


async def main():
    @dp.message(CommandStart())
    async def start(message: Message) -> None:
        await message.answer(inspect.cleandoc(f"""
            🚨 Alarm!
            📈 Your asset <strong>S&P500</strong> is down by <strong>3%</strong> since the last <strong>3 hours</strong>!
        """))

    @dp.inline_query()
    async def search(message: InlineQuery) -> None:
        print(message)
        await message.answer([
            InlineQueryResultArticle(
                id=str(random()),
                url='https://google.com',
                title="S&P500",
                # message='Some message',
                input_message_content=InputTextMessageContent(
                    message_text='Some text'
                )
            )
        ])

    bot = Bot(token=Config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
