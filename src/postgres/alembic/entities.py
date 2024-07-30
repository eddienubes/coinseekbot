from typing import Type

from crypto.entities.crypto_asset import CryptoAsset
from crypto.entities.crypto_asset_quote import CryptoAssetQuote
from crypto.entities.crypto_asset_tag import CryptoAssetTag
from crypto.entities.crypto_asset_to_asset_tag import CryptoAssetToAssetTag
from crypto.entities.crypto_watch import CryptoWatch
from exchanges.binance.entities import BinanceCryptoTradingPair, BinanceCryptoAsset
from telegram.tg_chat import TgChat
from telegram.tg_chat_to_user import TgChatToUser
from telegram.tg_user import TgUser


def register_entities() -> list[Type]:
    return [
        BinanceCryptoAsset,
        BinanceCryptoTradingPair,
        CryptoAsset,
        CryptoAssetTag,
        CryptoAssetToAssetTag,
        CryptoAssetQuote,
        CryptoWatch,
        TgChat,
        TgUser,
        TgChatToUser,
    ]
