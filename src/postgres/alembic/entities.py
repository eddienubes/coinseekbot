from typing import Type

from exchanges.binance.entities.binance_crypto_asset import BinanceCryptoAsset


def register_entities() -> list[Type]:
    return [
        BinanceCryptoAsset
    ]
