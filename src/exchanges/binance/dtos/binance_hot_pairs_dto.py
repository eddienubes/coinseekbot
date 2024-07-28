from .binance_base_dto import BinanceBaseDto
from .binance_hot_pair import BinanceHotPair
from dataclasses import dataclass


@dataclass
class BinanceHotPairsDto(BinanceBaseDto[list[BinanceHotPair]]):
    pass
