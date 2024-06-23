from .binance_hot_asset import BinanceHotAsset
from pydantic import BaseModel


class BinanceHotAssetsDto(BaseModel):
    code: str
    message: str | None
    messageDetail: str | None
    data: list[BinanceHotAsset]
    success: bool
