import inspect

from aiogram.types import Message, ChatMemberUpdated

from bot import TelegramBot
from aiogram.filters import Command, ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER, MEMBER

from bot.constants import SHIT_MEME_STICKER_ID
from telegram.tg_chat import TgChat
from telegram.tg_chats_repo import TgChatsRepo


@TelegramBot.router()
class BotGroupCommandsRouter:
    def __init__(self,
                 chats_repo: TgChatsRepo
                 ):
        self.__chats_repo = chats_repo

    @TelegramBot.handle_my_chat_member(ChatMemberUpdatedFilter(IS_MEMBER))
    async def bot_join(self, message: ChatMemberUpdated):
        # members = ','.join([a.username for a in message.new_chat_members])
        await self.__chats_repo.upsert(
            TgChat(
                tg_id=message.chat.id,
                type=message.chat.type,
                title=message.chat.title,
                username=message.chat.username,
                fullname=message.chat.full_name,
                is_forum=message.chat.is_forum,
                description=message.chat.description,
                bio=message.chat.bio,
                join_by_request=message.chat.join_by_request,
                invite_link=message.chat.invite_link
            )
        )

        await message.answer(inspect.cleandoc("""
            Tracky the bot has joined this chat. 👋
        """))
        await message.answer_sticker(sticker=SHIT_MEME_STICKER_ID)

    @TelegramBot.handle_message(Command('watch'))
    async def watch(self, message: Message):
        print(message)
        await message.answer_animation(animation=SHIT_MEME_STICKER_ID)
        await message.reply('Watch command')
