from typing import Type

from exchanges.binance.entities import BinanceCryptoTradingPair, BinanceCryptoAsset


def register_entities() -> list[Type]:
    return [
        BinanceCryptoAsset,
        BinanceCryptoTradingPair
    ]
