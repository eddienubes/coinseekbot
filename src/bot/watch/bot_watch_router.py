from aiogram.types import Message, CallbackQuery

from aiogram.filters import Command
from telegram.tg_chats_repo import TgChatsRepo
from .callbacks import WatchCallback

from .. import TelegramBot


@TelegramBot.router()
class BotWatchRouter:
    def __init__(self,
                 chats_repo: TgChatsRepo
                 ):
        self.__chats_repo = chats_repo

    @TelegramBot.handle_callback_query(WatchCallback.filter())
    async def watch_init(self, query: CallbackQuery, callback_data: WatchCallback):
        print(query, callback_data)
        pass

    @TelegramBot.handle_message(Command('watch'))
    async def watch(self, message: Message):
        await message.reply('Watch command')
