from aiogram import Bot
from aiogram.types import CallbackQuery

from crypto.crypto_assets_repo import CryptoAssetsRepo
from crypto.crypto_favourites_repo import CryptoFavouritesRepo
from crypto.crypto_watches_repo import CryptoWatchesRepo
from crypto.entities.crypto_favourite import CryptoFavourite, CryptoFavouriteStatus
from postgres import pg_session
from telegram.entities.tg_user import TgUser
from telegram.tg_chats_repo import TgChatsRepo
from bot.inline.views.callbacks import AddToFavouritesCb, RemoveFromFavouritesCb
from telegram.tg_users_repo import TgUsersRepo

from .. import TelegramBot
from ..inline.views.inline_query import render_query_result_reply_markup

import uuid

from datetime import datetime


@TelegramBot.router()
class BotFavouritesRouter:
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
        self.__crypto_favourites_repo = crypto_favourites_repo
        self.__tg_users_repo = tg_users_repo

    @pg_session
    @TelegramBot.handle_callback_query(AddToFavouritesCb.filter())
    async def add_to_favourites(self, query: CallbackQuery, callback_data: AddToFavouritesCb, bot: Bot):
        await callback_data.load()

        if query.from_user.id != callback_data.tg_user_id:
            return

        tg_user = TgUser(
            tg_id=query.from_user.id,
            is_bot=query.from_user.is_bot,
            first_name=query.from_user.first_name,
            last_name=query.from_user.last_name,
            username=query.from_user.username,
            language_code=query.from_user.language_code,
            is_premium=query.from_user.is_premium,
            added_to_attachment_menu=query.from_user.added_to_attachment_menu
        )

        tg_user = await self.__tg_users_repo.upsert(tg_user)

        await bot.answer_callback_query(
            callback_query_id=query.id,
            text='Added to Favourites!'
        )
        await bot.edit_message_reply_markup(
            inline_message_id=query.inline_message_id,
            reply_markup=await render_query_result_reply_markup(
                favourite=True,
                tg_user_id=tg_user.tg_id,
                asset_uuid=callback_data.asset_uuid
            )
        )

        favourite = CryptoFavourite(
            asset_uuid=uuid.UUID(callback_data.asset_uuid),
            tg_user_uuid=tg_user.uuid,
            status=CryptoFavouriteStatus.ACTIVE
        )

        await self.__crypto_favourites_repo.upsert(favourite)

    @pg_session
    @TelegramBot.handle_callback_query(RemoveFromFavouritesCb.filter())
    async def remove_from_favourites(self, query: CallbackQuery, callback_data: RemoveFromFavouritesCb, bot: Bot):
        await callback_data.load()

        if query.from_user.id != callback_data.tg_user_id:
            return

        tg_user = await self.__tg_users_repo.try_get_by_tg_id(callback_data.tg_user_id)

        await bot.answer_callback_query(
            callback_query_id=query.id,
            text='Removed from Favourites!',
        )
        await bot.edit_message_reply_markup(
            inline_message_id=query.inline_message_id,
            reply_markup=await render_query_result_reply_markup(
                favourite=False,
                tg_user_id=tg_user.tg_id,
                asset_uuid=callback_data.asset_uuid
            )
        )

        favourite = CryptoFavourite(
            asset_uuid=uuid.UUID(callback_data.asset_uuid),
            tg_user_uuid=tg_user.uuid,
            status=CryptoFavouriteStatus.INACTIVE
        )
        await self.__crypto_favourites_repo.upsert(favourite)
