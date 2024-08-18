from aiogram.types import Message, CallbackQuery

from aiogram.filters import Command

from crypto.crypto_assets_repo import CryptoAssetsRepo
from crypto.crypto_watches_repo import CryptoWatchesRepo
from crypto.crypto_favourites_repo import CryptoFavouritesRepo
from crypto.entities.crypto_watch import CryptoWatch, WatchInterval, CryptoWatchStatus
from telegram.tg_chats_repo import TgChatsRepo
from telegram.tg_users_repo import TgUsersRepo
from .bot_watch_service import BotWatchService
from .views.callbacks import WatchSelectIntervalCb, StopWatchingCb, StopWatchingConfirmationCb, StartWatchingCb, \
    WatchlistFavouritesCb, WatchlistPageCb
from .views.views import render_watch_select_text, render_start_watching_list, \
    render_watchlist_text, render_watchlist, \
    render_stop_watching_confirm_text, render_stop_watching_confirm_reply_markup, WATCH_INTERVALS_TEXT
from .. import TelegramBot
import uuid


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
                text=render_watchlist_text()
            )
            return

        watchlist = await self.__crypto_watches_repo.get_watchlist(
            tg_user_uuid=tg_user.uuid,
            tg_chat_uuid=tg_user.chat.uuid
        )

        await message.reply(
            text=render_watchlist_text(),
            reply_markup=render_watchlist(
                tg_user_id=message.from_user.id,
                watchlist=watchlist
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

        watchlist = await self.__crypto_watches_repo.get_watchlist(
            tg_user_uuid=tg_user.uuid,
            tg_chat_uuid=tg_user.chat.uuid
        )

        await query.message.edit_text(
            text=render_watchlist_text(),
            reply_markup=render_watchlist(
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

        watch = await self.__crypto_watches_repo.upsert(
            CryptoWatch(
                asset_uuid=asset.uuid,
                tg_chat_uuid=tg_user.chat.uuid,
                interval=WatchInterval(callback_data.interval),
                status=CryptoWatchStatus.ACTIVE,
                next_execution_at=None
            )
        )

        watchlist = await self.__crypto_watches_repo.get_watchlist(
            tg_user_uuid=tg_user.uuid,
            tg_chat_uuid=tg_user.chat.uuid
        )

        await query.message.edit_text(
            text=render_watchlist_text(),
            reply_markup=render_watchlist(
                tg_user_id=query.from_user.id,
                watchlist=watchlist
            )
        )

        await query.answer(
            f'Started watching {asset.name}! You will receive notifications once in {WATCH_INTERVALS_TEXT[watch.interval]}.')

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

        watchlist = await self.__crypto_watches_repo.get_watchlist(
            tg_user_uuid=tg_user.uuid,
            tg_chat_uuid=tg_user.chat.uuid
        )

        await query.message.edit_text(
            text=render_watchlist_text(),
            reply_markup=render_watchlist(
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

        watchlist = await self.__crypto_watches_repo.get_watchlist(
            tg_user_uuid=tg_user.uuid,
            tg_chat_uuid=tg_user.chat.uuid,
            offset=callback_data.offset
        )

        await query.message.edit_text(
            text=render_watchlist_text(),
            reply_markup=render_watchlist(
                tg_user_id=tg_user.tg_id,
                watchlist=watchlist
            )
        )
