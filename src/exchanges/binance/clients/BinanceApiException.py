from pprint import pformat
from typing import Mapping


class BinanceApiException(Exception):
    def __init__(self, message: str = None, obj: Mapping = None, *args):
        extra = pformat(obj) if obj is not None else ''

        message = f'{message} {extra}' if message else f'Binance API error occurred. {extra}'

        super().__init__(message, *args)
