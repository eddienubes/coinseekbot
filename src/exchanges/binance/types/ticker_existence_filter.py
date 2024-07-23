import dataclasses

from ..entities.binance_crypto_asset import BinanceCryptoAsset


@dataclasses.dataclass
class TickerExistenceFilter:
    hits: list[BinanceCryptoAsset]
    misses: list[str]
