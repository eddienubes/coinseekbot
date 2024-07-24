import dataclasses

from utils import SearchDto
from ..entities.binance_crypto_asset import BinanceCryptoAsset


@dataclasses.dataclass
class TickerExistenceFilter(SearchDto[BinanceCryptoAsset, str]):
    pass
