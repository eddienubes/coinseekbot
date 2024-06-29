from exchanges.binance import BinanceAssetsQueryApi


class BinanceAssetsQueryService:

    def __init__(self, binance_client: BinanceAssetsQueryApi):
        self.client = binance_client
        self.cache = None

    def get_hot_assets(self):
        return self.client.get_hot_assets()
