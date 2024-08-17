from typing import Any

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from aiogram.filters import Command

from crypto.crypto_assets_repo import CryptoAssetsRepo
from crypto.crypto_watches_repo import CryptoWatchesRepo
from crypto.crypto_favourites_repo import CryptoFavouritesRepo
from crypto.entities.crypto_favourite import CryptoFavourite
from crypto.entities.crypto_watch import CryptoWatch, WatchInterval, CryptoWatchStatus
from telegram.entities.tg_chat import TgChat
from telegram.tg_chats_repo import TgChatsRepo
from telegram.tg_users_repo import TgUsersRepo
from utils import Pageable
from .bot_watch_service import BotWatchService
from .views.callbacks import WatchSelectIntervalCb, StopWatchingCb, StopWatchingConfirmationCb, StartWatchingCb, \
    WatchlistFavouritesCb, WatchlistPageCb
from .views.views import render_watch_select_text, render_start_watching_list, \
    render_favourite_list_text, render_favourites_list, \
    render_stop_watching_confirm_text, render_stop_watching_confirm_reply_markup
from .. import TelegramBot
import uuid
from datetime import datetime


@TelegramBot.router()
class BotWatchRouter:
    def __init__(
            self,
            chats_repo: TgChatsRepo,
            assets_repo: CryptoAssetsRepo,
            crypto_watches_repo: CryptoWatchesRepo,
            crypto_favourites_repo: CryptoFavouritesRepo,
            tg_users_repo: TgUsersRepo,
            bot_watch_service: BotWatchService
    ):
        self.__chats_repo = chats_repo
        self.__assets_repo = assets_repo
        self.__crypto_watches_repo = crypto_watches_repo
        self.__crypto_favorites_repo = crypto_favourites_repo
        self.__tg_users_repo = tg_users_repo
        self.__bot_watch_service = bot_watch_service

    @TelegramBot.handle_message(Command('watch'))
    async def watch_list_favourites_command(self, message: Message):

        tg_user = await self.__tg_users_repo.get_by_tg_id_with_chat(
            tg_user_id=message.from_user.id,
            tg_chat_id=message.chat.id
        )

        # If there is no user, that means no crypto favourites
        if not tg_user:
            await message.reply(
                text=render_favourite_list_text()
            )
            return

        favourites = await self.get_watchlist(
            tg_user_uuid=tg_user.uuid,
            tg_chat_uuid=tg_user.chat.uuid
        )

        await message.reply(
            text=render_favourite_list_text(),
            reply_markup=render_favourites_list(
                tg_user_id=message.from_user.id,
                watchlist=favourites
            )
        )

    @TelegramBot.handle_callback_query(WatchlistFavouritesCb.filter())
    async def watch_list_favourites_cb(self, query: CallbackQuery, callback_data: WatchlistFavouritesCb):
        if query.from_user.id != callback_data.tg_user_id:
            return

        tg_user = await self.__tg_users_repo.get_by_tg_id_with_chat(
            tg_user_id=query.from_user.id,
            tg_chat_id=query.message.chat.id
        )

        watchlist = await self.get_watchlist(
            tg_user_uuid=tg_user.uuid,
            tg_chat_uuid=tg_user.chat.uuid
        )

        await query.message.edit_text(
            text=render_favourite_list_text(),
            reply_markup=render_favourites_list(
                tg_user_id=query.from_user.id,
                watchlist=watchlist
            )
        )

    @TelegramBot.handle_callback_query(WatchSelectIntervalCb.filter())
    async def select_interval(self, query: CallbackQuery, callback_data: WatchSelectIntervalCb):
        if query.from_user.id != callback_data.tg_user_id:
            return

        asset = await self.__assets_repo.try_get_by_uuid(callback_data.asset_uuid)

        await query.message.edit_text(
            text=render_watch_select_text(asset),
            reply_markup=await render_start_watching_list(
                tg_user_id=query.from_user.id,
                asset_uuid=callback_data.asset_uuid
            )
        )

    @TelegramBot.handle_callback_query(StartWatchingCb.filter())
    async def start_watching(self, query: CallbackQuery, callback_data: StartWatchingCb):
        await callback_data.load()

        if query.from_user.id != callback_data.tg_user_id:
            return

        asset = await self.__assets_repo.try_get_by_uuid(callback_data.asset_uuid)
        tg_user = await self.__tg_users_repo.get_by_tg_id_with_chat(
            tg_user_id=query.from_user.id,
            tg_chat_id=query.message.chat.id
        )

        await self.__crypto_watches_repo.upsert(
            CryptoWatch(
                asset_uuid=asset.uuid,
                tg_chat_uuid=tg_user.chat.uuid,
                interval=WatchInterval(callback_data.interval),
                status=CryptoWatchStatus.ACTIVE,
                next_execution_at=None
            )
        )

        watchlist = await self.get_watchlist(
            tg_user_uuid=tg_user.uuid,
            tg_chat_uuid=tg_user.chat.uuid
        )

        await query.message.edit_text(
            text=render_favourite_list_text(),
            reply_markup=render_favourites_list(
                tg_user_id=query.from_user.id,
                watchlist=watchlist
            )
        )

    @TelegramBot.handle_callback_query(StopWatchingConfirmationCb.filter())
    async def stop_watching_confirmation(
            self, query: CallbackQuery,
            callback_data: StopWatchingConfirmationCb
    ):
        if query.from_user.id != callback_data.tg_user_id:
            return

        asset = await self.__assets_repo.try_get_by_uuid(callback_data.asset_uuid)

        await query.message.edit_text(
            text=render_stop_watching_confirm_text(
                asset=asset
            ),
            reply_markup=render_stop_watching_confirm_reply_markup(
                tg_user_id=query.from_user.id,
                asset_uuid=callback_data.asset_uuid
            )
        )

    @TelegramBot.handle_callback_query(StopWatchingCb.filter())
    async def stop_watching(self, query: CallbackQuery, callback_data: StopWatchingCb):
        if query.from_user.id != callback_data.tg_user_id:
            return

        tg_user = await self.__tg_users_repo.get_by_tg_id_with_chat(
            tg_user_id=query.from_user.id,
            tg_chat_id=query.message.chat.id
        )

        watch = CryptoWatch(
            asset_uuid=uuid.UUID(callback_data.asset_uuid),
            tg_chat_uuid=tg_user.chat.uuid,
            status=CryptoWatchStatus.INACTIVE
        )

        await self.__crypto_watches_repo.update(watch, [CryptoWatch.asset_uuid, CryptoWatch.tg_chat_uuid])

        watchlist = await self.get_watchlist(
            tg_user_uuid=tg_user.uuid,
            tg_chat_uuid=tg_user.chat.uuid
        )

        await query.message.edit_text(
            text=render_favourite_list_text(),
            reply_markup=render_favourites_list(
                tg_user_id=tg_user.tg_id,
                watchlist=watchlist
            )
        )

        await query.answer('Stopped watching.')

    @TelegramBot.handle_callback_query(WatchlistPageCb.filter())
    async def watchlist(self, query: CallbackQuery, callback_data: WatchlistPageCb):
        if query.from_user.id != callback_data.tg_user_id:
            return

        tg_user = await self.__tg_users_repo.get_by_tg_id_with_chat(
            tg_user_id=query.from_user.id,
            tg_chat_id=query.message.chat.id
        )

        watchlist = await self.get_watchlist(
            tg_user_uuid=tg_user.uuid,
            tg_chat_uuid=tg_user.chat.uuid,
            offset=callback_data.offset
        )

        await query.message.edit_text(
            text=render_favourite_list_text(),
            reply_markup=render_favourites_list(
                tg_user_id=tg_user.tg_id,
                watchlist=watchlist
            )
        )

    async def get_watchlist(self,
                            tg_user_uuid: uuid.UUID,
                            tg_chat_uuid: uuid.UUID,
                            offset: int = 0,
                            limit: int = 5
                            ) -> Pageable[CryptoWatch | CryptoFavourite]:

        favourites = await self.__crypto_favorites_repo.get_by_tg_user_uuid_with_assets(
            tg_user_uuid=tg_user_uuid,
            tg_chat_uuid=tg_chat_uuid,
            offset=offset,
            limit=limit
        )

        offset_left = max(offset - (favourites.total - len(favourites.hits)), 0)
        limit_left = max(limit - len(favourites.hits), 0)

        watches = await self.__crypto_watches_repo.get_with_joins_by_chat(
            tg_chat_uuid=tg_chat_uuid,
            offset=offset_left,
            asset_uuids_not_in=[f.asset_uuid for f in favourites.hits],
            limit=limit_left
        )

        hits = [*favourites.hits, *watches.hits]

        def _(x: CryptoWatch | CryptoFavourite):
            if isinstance(x, CryptoWatch) and x.status == CryptoWatchStatus.ACTIVE:
                print('pushed watch to front', x.asset.name)
                return 1, x.updated_at
            if isinstance(x, CryptoFavourite) and x.watch and x.watch.status == CryptoWatchStatus.ACTIVE:
                print('pushed fav to front', x.asset.name)
                return 1, x.updated_at
            # 0 - primary sort key, x.updated_at or False (to keep order)- secondary sort key
            return 0, False

        hits = sorted(hits, key=lambda x: _(x), reverse=True)

        return Pageable(
            hits=hits,
            total=favourites.total + watches.total,
            limit=limit,
            offset=offset
        )
