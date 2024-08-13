from crypto.crypto_assets_repo import CryptoAssetsRepo
from crypto.crypto_favourites_repo import CryptoFavouritesRepo
from crypto.crypto_watches_repo import CryptoWatchesRepo
from telegram.tg_chats_repo import TgChatsRepo
from telegram.tg_users_repo import TgUsersRepo


class BotWatchService:
    def __init__(self,
                 chats_repo: TgChatsRepo,
                 assets_repo: CryptoAssetsRepo,
                 crypto_watches_repo: CryptoWatchesRepo,
                 crypto_favourites_repo: CryptoFavouritesRepo,
                 tg_users_repo: TgUsersRepo
                 ):
        self.__chats_repo = chats_repo
        self.__assets_repo = assets_repo
        self.__crypto_watches_repo = crypto_watches_repo
        self.__crypto_favorites_repo = crypto_favourites_repo
        self.__tg_users_repo = tg_users_repo
