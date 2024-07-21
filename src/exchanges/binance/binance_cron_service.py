from exchanges.binance import BinanceAssetsQueryApi
from exchanges.binance.binance_crypto_asset_repo import BinanceCryptoAssetRepo


class BinanceCronService:
    def __init__(self, binance_assets_query_api: BinanceAssetsQueryApi,
                 binance_crypto_assets_repo: BinanceCryptoAssetRepo):
        self.__binance_assets_query_api = binance_assets_query_api

    async def ingest_assets(self):
        """Create available on binance assets"""
        assets = await self.__binance_assets_query_api.get_all_assets()

        entities = []
