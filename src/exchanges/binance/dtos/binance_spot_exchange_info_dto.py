import dataclasses

from dataclasses_json import DataClassJsonMixin

from .binance_spot_exchange_info_symbol import BinanceSpotExchangeInfoSymbol


@dataclasses.dataclass
class BinanceSpotExchangeInfoDto(DataClassJsonMixin):
    timezone: str
    serverTime: int
    rateLimits: list
    exchangeFilters: list
    symbols: list[BinanceSpotExchangeInfoSymbol]
