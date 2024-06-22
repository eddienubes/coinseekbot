from dataclasses import dataclass


@dataclass(frozen=True)
class BinanceHotAsset:
    assetCode: str
    assetName: str
    logoUrl: str
    chartLine: object
    symbol: str
    circulatingSupply: object
