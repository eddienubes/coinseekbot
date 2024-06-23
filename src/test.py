import asyncio
from common.binance import BinanceAssetsQueryApi


async def main():
    binance_assets_query_api = BinanceAssetsQueryApi()

    assets = await binance_assets_query_api.get_hot_assets()

    print(assets)


asyncio.run(main())
