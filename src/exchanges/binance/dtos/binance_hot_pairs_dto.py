from .binance_hot_pair import BinanceHotPair
from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin


@dataclass
class BinanceHotPairsDto(DataClassJsonMixin):
    code: str
    message: str | None
    messageDetail: str | None
    data: list[BinanceHotPair]
    success: bool
