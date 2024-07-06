from exchanges.binance.dtos.binance_asset import BinanceAsset
from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin


@dataclass
class BinanceAllAssetsDto(DataClassJsonMixin):
    code: str
    message: str | None
    messageDetail: str | None
    data: list[BinanceAsset]
    success: bool
