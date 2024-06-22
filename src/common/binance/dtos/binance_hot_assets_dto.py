from dataclasses import dataclass
from binance_hot_asset import BinanceHotAsset


@dataclass(frozen=True)
class BinanceHotAssetsDto:
    code: str
    message: str | None
    messageDetail: str | None
    data: list[BinanceHotAsset]
    success: bool
