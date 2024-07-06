from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin


@dataclass
class BinanceAsset(DataClassJsonMixin):
    id: str
    assetCode: str
    assetName: str
    unit: str
    commissionRate: float
    isLegalMoney: bool
    logoUrl: str
    fullLogoUrl: str
    tags: list[str]
    delisted: bool
    preDelist: bool
