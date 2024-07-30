from yahoo.yahoo_api_client import YahooApiClient


# from apscheduler.schedulers.asyncio import AsyncIOScheduler


class Collector:
    def __init__(self, yahoo_api_client: YahooApiClient):
        self.yahoo_api_client = yahoo_api_client

    @staticmethod
    # @AsyncIOScheduler.()
    def collect_yahoo_ticker_history(self) -> None:
        # TODO: Get symbols from database
        symbols = ['AAPL']
        interval = '1m'
        period = '1d'

        history = self.yahoo_api_client.get_ticker_history(symbols, period=period, interval=interval)

        history.to_csv('history.csv')
