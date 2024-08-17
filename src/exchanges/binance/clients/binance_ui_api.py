import functools
import logging

from aiogram.client.session import aiohttp

from utils import CDict, retry
from .BinanceApiException import BinanceApiException
from ..dtos.binance_all_assets_dto import BinanceAllAssetsDto
from ..dtos.binance_all_coins_dto import BinanceAllCoinsDto, BinanceAllCoinsBody
from ..dtos.binance_hot_pairs_dto import BinanceHotPairsDto


class BinanceUiApi:
    def __init__(self):
        self.session = aiohttp.ClientSession(base_url='https://www.binance.com')
        self.__logger = logging.getLogger(self.__class__.__name__)

    async def get_all_assets(self) -> BinanceAllAssetsDto:
        async with self.session.get('/bapi/asset/v2/public/asset/asset/get-all-asset') as res:
            data = await res.json()
            return BinanceAllAssetsDto.from_dict(data)

    async def get_hot_pairs(self) -> BinanceHotPairsDto:
        async with self.session.get('/bapi/composite/v1/public/market/hot-coins?currency=USD') as res:
            data = await res.json()
            return BinanceHotPairsDto.from_dict(data)

    async def get_all_coins(self, offset: int = 1, limit: int = 5000) -> BinanceAllCoinsBody:
        self.__logger.info(f'get_all_coins: with offset {offset} and limit {limit}')

        if limit < 5 or limit > 5000:
            # Causes 500 sometimes
            raise ValueError('Limit must be at least 5 and at most 5000')

        params = {
            'start': offset,
            'limit': limit
        }

        @functools.wraps(self.get_all_coins)
        async def _():
            async with self.session.get('/bapi/composite/v1/public/promo/cmc/cryptocurrency/listings/latest',
                                        params=params) as res:
                logging.info(f'get_all_coins: status {res.status}, content_type: {res.content_type}')

                data = CDict(await res.json())

                success = data.data.success

                if not success:
                    raise BinanceApiException('Failed to fetch all coins', data.data.body.status)

                dto = BinanceAllCoinsDto.from_dict(data)

                return dto.data.body

        # Sometimes binance returns 500, retrying
        return await retry(_, max_retries=10, jitter=True, backoff=1.18)

    async def on_module_destroy(self):
        await self.session.__aexit__(None, None, None)
