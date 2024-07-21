from .binance_assets_query_api import BinanceAssetsQueryApi
from .binance_crypto_asset_repo import BinanceCryptoAssetRepo

print('executed some code')


class BinanceCronService:
    def __init__(self, binance_assets_query_api: BinanceAssetsQueryApi,
                 binance_crypto_assets_repo: BinanceCryptoAssetRepo):
        self.__binance_assets_query_api = binance_assets_query_api
        self.__binance_crypto_assets_repo = binance_crypto_assets_repo

    async def ingest_assets(self):
        """Create available on binance assets"""
        assets = await self.__binance_assets_query_api.get_all_assets()

        hm = dict()

        for asset in assets.data:
            hm[asset.assetCode] = asset

        non_existing_tickers = await self.__binance_crypto_assets_repo.get_non_existent_tickers(list(hm.keys()))

        print(non_existing_tickers)
