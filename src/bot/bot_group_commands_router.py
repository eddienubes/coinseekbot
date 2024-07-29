from aiogram.types import Message, ChatMemberUpdated

from bot import TelegramBot
from aiogram.filters import Command, ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER, MEMBER

from tg_users.tg_chats_repo import TgChatsRepo


@TelegramBot.router()
class BotGroupCommandsRouter:
    def __init__(self,
                 chats_repo: TgChatsRepo
                 ):
        self.__chats_repo = chats_repo

    @TelegramBot.handle_my_chat_member(ChatMemberUpdatedFilter(IS_MEMBER))
    async def bot_join(self, message: ChatMemberUpdated):
        # members = ','.join([a.username for a in message.new_chat_members])
        self.__chats_repo.add(
            TgChatsRepo(

            )
        )

        await message.answer(f'Welcome to the group!')

    @TelegramBot.handle_message(Command('watch'))
    async def watch(self, message: Message):
        print(message)
        await message.reply('Watch command')
