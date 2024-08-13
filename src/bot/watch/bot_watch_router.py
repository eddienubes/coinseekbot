from aiogram import Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.filters import Command

from crypto.crypto_assets_repo import CryptoAssetsRepo
from crypto.crypto_watches_repo import CryptoWatchesRepo
from crypto.crypto_favourites_repo import CryptoFavouritesRepo
from crypto.entities.crypto_watch import CryptoWatch
from telegram.tg_chats_repo import TgChatsRepo
from bot.inline.views.callbacks import AddToFavouritesCb
from telegram.tg_users_repo import TgUsersRepo
from .views.callbacks import WatchSelectIntervalCb
from .views.reply_markups import render_watch_select_interval, render_watch_select_text

from .. import TelegramBot


@TelegramBot.router()
class BotWatchRouter:
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

    @TelegramBot.handle_message(Command('watch'))
    async def watch(self, message: Message):
        tg_user = await self.__tg_users_repo.get_by_tg_id(message.from_user.id)

        # If there is no user, that means no crypto favourites
        if not tg_user:
            await message.reply(
                text='Watch command'
            )
            return

        favourites = await self.__crypto_favorites_repo.get_by_tg_user_uuid_with_assets(
            tg_user_uuid=tg_user.uuid
        )

        btns = [[InlineKeyboardButton(
            text=f'{fav.asset.ticker} - {fav.asset.name}',
            callback_data='askldfj'
        )] for fav in favourites.hits]

        await message.reply(
            text='Watch command with assets',
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    *btns
                ]
            )

        )
