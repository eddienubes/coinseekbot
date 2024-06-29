import asyncio
import logging

from bot import TelegramBot
from container import Container


async def main():
    logging.basicConfig(level=logging.DEBUG)

    container = Container()
    await container.init()
    tg_bot = container.get(TelegramBot)
    await tg_bot.start()


if __name__ == "__main__":
    asyncio.run(main())
