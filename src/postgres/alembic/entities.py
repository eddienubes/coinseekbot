from typing import Type

from crypto.entities.crypto_asset import CryptoAsset
from crypto.entities.crypto_asset_tag import CryptoAssetTag
from crypto.entities.crypto_asset_to_asset_tag import crypto_to_asset_tag
from exchanges.binance.entities import BinanceCryptoTradingPair, BinanceCryptoAsset


def register_entities() -> list[Type]:
    return [
        BinanceCryptoAsset,
        BinanceCryptoTradingPair,
        CryptoAsset,
        CryptoAssetTag,
        crypto_to_asset_tag
    ]
