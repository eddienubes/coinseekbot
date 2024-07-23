import asyncio

import aiohttp
from binance.spot import Spot

from .dtos.binance_hot_pairs_dto import BinanceHotPairsDto
from .dtos.binance_all_assets_dto import BinanceAllAssetsDto
from .dtos.binance_spot_exchange_info_dto import BinanceSpotExchangeInfoDto


class BinanceAssetsQueryApi:
    def __init__(self):
        self.session = aiohttp.ClientSession(base_url='https://www.binance.com')
        self.__spot_client = Spot()

    async def get_hot_pairs(self) -> BinanceHotPairsDto:
        async with self.session.get('/bapi/composite/v1/public/market/hot-coins?currency=USD') as res:
            data = await res.json()
            return BinanceHotPairsDto.from_dict(data)

    async def get_all_pairs(self) -> BinanceSpotExchangeInfoDto:
        data = await asyncio.to_thread(self.__spot_client.exchange_info)
        return BinanceSpotExchangeInfoDto.from_dict(data)

    async def get_all_assets(self) -> BinanceAllAssetsDto:
        async with self.session.get('/bapi/asset/v2/public/asset/asset/get-all-asset') as res:
            data = await res.json()
            return BinanceAllAssetsDto.from_dict(data)

    async def on_module_destroy(self):
        await self.session.close()
