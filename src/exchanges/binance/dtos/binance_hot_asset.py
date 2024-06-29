import pathlib

from pydantic import BaseModel, field_validator


class BinanceHotAsset(BaseModel):
    assetCode: str
    assetName: str
    logoUrl: str
    chartLine: object
    symbol: str
    circulatingSupply: object

    # PEPE logo url should be PEPE.png
    @field_validator('logoUrl', mode='before')
    @classmethod
    def validate_logo_url(cls, v: str) -> str:
        path = pathlib.Path(v)
        if not path.suffix:
            return f'{v}.png'
        return v
