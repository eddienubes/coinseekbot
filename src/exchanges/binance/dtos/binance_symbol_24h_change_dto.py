import dataclasses

from dataclasses_json import DataClassJsonMixin


@dataclasses.dataclass
class BinanceSymbol24hChangeDto(DataClassJsonMixin):
    symbol: str
    lastPrice: str
    priceChangePercent: str
    priceChange: str
    askPrice: str
    askQty: str
    bidPrice: str
    bidQty: str
    closeTime: int
    count: int
    firstId: int
    highPrice: str
    lastId: int
    lastQty: str
    lowPrice: str
    openPrice: str
    openTime: int
    prevClosePrice: str
    quoteVolume: str
    volume: str
    weightedAvgPrice: str
