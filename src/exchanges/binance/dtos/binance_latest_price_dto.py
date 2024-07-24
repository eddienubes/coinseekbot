import dataclasses

from dataclasses_json import DataClassJsonMixin


@dataclasses.dataclass
class BinanceLatestPriceDto(DataClassJsonMixin):
    # uppsercase
    symbol: str
    price: str
