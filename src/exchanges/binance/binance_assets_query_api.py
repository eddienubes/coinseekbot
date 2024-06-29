import aiohttp

from .dtos.binance_hot_assets_dto import BinanceHotAssetsDto


class BinanceAssetsQueryApi:
    # Remember, aiohttp session has to be initialized within async context
    def __init__(self):
        self.session = aiohttp.ClientSession(base_url='https://www.binance.com')

    async def get_hot_assets(self) -> BinanceHotAssetsDto:
        res = await self.session.get('/bapi/composite/v1/public/market/hot-coins?currency=USD')
        data = await res.json()
        return BinanceHotAssetsDto.model_validate(data)

    async def on_module_destroy(self):
        await self.session.close()
