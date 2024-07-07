from exchanges.binance import BinanceAssetsQueryApi


class BinanceCronService:
    def __init__(self, binance_assets_query_api: BinanceAssetsQueryApi):
        self.__binance_assets_query_api = binance_assets_query_api
