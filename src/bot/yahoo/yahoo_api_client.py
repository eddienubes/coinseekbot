from yahooquery import Ticker
import pandas as pd


class YahooApiClient:
    def get_ticker_history(self, ticker: str | list, period='max', interval='1d') -> pd.DataFrame:
        ticker = self.__get_ticker(ticker)

        history = ticker.history(period=period, interval=interval)
        return history

    def __get_ticker(self, asset: str | list[str]) -> Ticker:
        return Ticker(asset, asynchronous=True)
