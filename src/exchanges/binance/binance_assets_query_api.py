from typing import Any

import aiohttp
from binance.spot import Spot

from .dtos.binance_hot_pairs_dto import BinanceHotPairsDto
from .dtos.binance_all_assets_dto import BinanceAllAssetsDto


class BinanceAssetsQueryApi:
    # Remember, aiohttp session has to be initialized within async context
    def __init__(self):
        self.session = aiohttp.ClientSession(base_url='https://www.binance.com')

    async def get_hot_pairs(self) -> BinanceHotPairsDto:
        async with self.session.get('/bapi/composite/v1/public/market/hot-coins?currency=USD') as res:
            data = await res.json()
            return BinanceHotPairsDto.from_dict(data)

    async def get_all_pairs(self) -> Any:
        client = Spot()
        # noinspection PyArgumentList
        data = client.exchange_info()
        print(data)

    async def get_all_assets(self) -> BinanceAllAssetsDto:
        async with self.session.get('/bapi/asset/v2/public/asset/asset/get-all-asset') as res:
            data = await res.json()
            return BinanceAllAssetsDto.from_dict(data)

    async def on_module_destroy(self):
        await self.session.close()
