import asyncio
import logging

from instances import tg_bot, assets_query_api, init


async def main():
    logging.basicConfig(level=logging.INFO)

    await init()
    print("Starting bot...")
    await tg_bot.start(some_service=assets_query_api)


if __name__ == "__main__":
    asyncio.run(main())
