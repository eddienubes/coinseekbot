from .binance_asset import BinanceAsset
from dataclasses import dataclass

from .binance_base_dto import BinanceBaseDto


@dataclass
class BinanceAllAssetsDto(BinanceBaseDto[list[BinanceAsset]]):
    pass
