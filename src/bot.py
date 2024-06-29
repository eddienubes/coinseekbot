import asyncio
import logging

from bot import TelegramBot
from instances import init


async def main():
    logging.basicConfig(level=logging.DEBUG)

    container = await init()
    tg_bot = container.get(TelegramBot)
    await tg_bot.start()


if __name__ == "__main__":
    asyncio.run(main())
