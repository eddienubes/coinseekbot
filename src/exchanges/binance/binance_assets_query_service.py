from exchanges.binance import BinanceAssetsQueryApi
from exchanges.binance.dtos.binance_hot_pair import BinanceHotPair
from exchanges.binance.dtos.binance_hot_pairs_dto import BinanceHotPairsDto
from exchanges.binance.dtos.binance_all_assets_dto import BinanceAllAssetsDto
from exchanges.binance.dtos.binance_asset import BinanceAsset
from redis_client import RedisService


class BinanceAssetsQueryService:
    def __init__(self, binance_client: BinanceAssetsQueryApi, redis_service: RedisService):
        self.__client = binance_client
        self.__redis = redis_service
        self.__hot_pairs_key = "binance-hot-pairs"
        self.__all_assets_key = "binance-all-assets"
        self.__cache_expires_at = 60 * 60 * 2  # 2 hours

    async def get_hot_pairs(self) -> list[BinanceHotPair]:
        hot_assets = await self.__redis.get(self.__hot_pairs_key)
        if hot_assets:
            model = BinanceHotPairsDto.from_json(hot_assets)
            return model.data
        else:
            pairs = await self.__client.get_hot_pairs()

            json_str = pairs.to_json()

            await self.__redis.set(
                self.__hot_pairs_key,
                json_str,
                ex_s=self.__cache_expires_at
            )

            return pairs.data

    async def get_all_assets(self) -> list[BinanceAsset]:
        all_assets = await self.__redis.get(self.__all_assets_key)
        if all_assets:
            model = BinanceAllAssetsDto.from_json(all_assets)
            return model.data
        else:
            assets = await self.__client.get_all_assets()

            json_str = assets.to_json()

            await self.__redis.set(
                self.__all_assets_key,
                json_str,
                ex_s=self.__cache_expires_at
            )

            return assets.data
