import pathlib

from typing import List

from exchanges.binance import BinanceAssetsQueryApi
from exchanges.binance.dtos.binance_hot_asset import BinanceHotAsset
from exchanges.binance.dtos.binance_hot_assets_dto import BinanceHotAssetsDto
from redis_client import RedisService


class BinanceAssetsQueryService:
    def __init__(self, binance_client: BinanceAssetsQueryApi, redis_service: RedisService):
        self.__client = binance_client
        self.__redis = redis_service
        self.__hot_assets_key = "binance_hot_assets"
        self.__hot_assets_expires_at = 60 * 60 * 2  # 2 hours

    async def get_hot_assets(self) -> List[BinanceHotAsset]:
        hot_assets = await self.__redis.get(self.__hot_assets_key)
        if hot_assets:
            model = BinanceHotAssetsDto.model_validate_json(hot_assets)
            return model.data
        else:
            assets = await self.__client.get_hot_assets()

            json_str = assets.model_dump_json()

            await self.__redis.set(
                self.__hot_assets_key,
                json_str,
                ex_s=self.__hot_assets_expires_at
            )

            return assets.data
