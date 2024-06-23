from pydantic import BaseModel


class BinanceHotAsset(BaseModel):
    assetCode: str
    assetName: str
    logoUrl: str
    chartLine: object
    symbol: str
    circulatingSupply: object
