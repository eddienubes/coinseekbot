import dataclasses

from exchanges.binance.dtos.binance_symbol_24h_change_dto import BinanceSymbol24hChangeDto
from utils import SearchDto


@dataclasses.dataclass
class BinanceTradingPairPriceChangeSearch(SearchDto[BinanceSymbol24hChangeDto, str]):
    pass
