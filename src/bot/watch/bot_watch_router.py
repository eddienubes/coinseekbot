from aiogram import Bot
from aiogram.types import Message, CallbackQuery

from aiogram.filters import Command
from telegram.tg_chats_repo import TgChatsRepo
from bot.inline.views.callbacks import WatchCb
from .views.reply_markups import watch_select_interval

from .. import TelegramBot


@TelegramBot.router()
class BotWatchRouter:
    def __init__(self,
                 chats_repo: TgChatsRepo
                 ):
        self.__chats_repo = chats_repo

    @TelegramBot.handle_callback_query(WatchCb.filter())
    async def watch_select_interval(self, query: CallbackQuery, callback_data: WatchCb, bot: Bot):
        if query.from_user.id != callback_data.tg_user_id:
            return

        await bot.edit_message_reply_markup(
            inline_message_id=query.inline_message_id,
            reply_markup=watch_select_interval(
                asset_uuid=callback_data.asset_uuid,
                tg_user_id=callback_data.tg_user_id
            )
        )

    @TelegramBot.handle_message(Command('watch'))
    async def watch(self, message: Message):
        await message.reply('Watch command')
