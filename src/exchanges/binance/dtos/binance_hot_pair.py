from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin


@dataclass
class BinanceHotPair(DataClassJsonMixin):
    assetCode: str
    assetName: str
    logoUrl: str
    chartLine: object
    symbol: str
    circulatingSupply: object
