import asyncio

import aiohttp

from dtos.binance_hot_assets_dto import BinanceHotAssetsDto


class BinanceAssetsApiClient:
    def __init__(self):
        self.session = aiohttp.ClientSession(base_url='https://www.binance.com')

    def __del__(self):
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self.session.close())
            else:
                loop.run_until_complete(self.session.close())
        except Exception as e:
            raise e

    async def get_hot_assets(self) -> BinanceHotAssetsDto:
        res = await self.session.get('/bapi/composite/v1/public/market/hot-coins?currency=USD')

        return await res.json()
