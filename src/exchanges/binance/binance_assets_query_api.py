import aiohttp

from .dtos.binance_hot_pairs_dto import BinanceHotPairsDto
from .dtos.binance_all_assets_dto import BinanceAllAssetsDto


class BinanceAssetsQueryApi:
    # Remember, aiohttp session has to be initialized within async context
    def __init__(self):
        self.session = aiohttp.ClientSession(base_url='https://www.binance.com')

    async def get_hot_pairs(self) -> BinanceHotPairsDto:
        res = await self.session.get('/bapi/composite/v1/public/market/hot-coins?currency=USD')
        data = await res.json()
        return BinanceHotPairsDto.from_dict(data)

    async def get_all_assets(self) -> BinanceAllAssetsDto:
        res = await self.session.get('/bapi/asset/v2/public/asset/asset/get-all-asset')
        data = await res.json()
        return BinanceAllAssetsDto.from_dict(data)

    async def on_module_destroy(self):
        await self.session.close()
