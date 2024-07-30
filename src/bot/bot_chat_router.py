import inspect

from aiogram.enums import ParseMode
from aiogram.types import ChatMemberUpdated

from bot import TelegramBot
from aiogram.filters import ChatMemberUpdatedFilter, IS_MEMBER

from bot.constants import SHIT_MEME_STICKER_ID
from telegram.tg_chat import TgChat
from telegram.tg_chats_repo import TgChatsRepo


@TelegramBot.router()
class BotChatRouter:
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

        await message.answer_sticker(sticker=SHIT_MEME_STICKER_ID)
        await message.answer(inspect.cleandoc("""
            What's up Bitcoin holders, condolences to the rest 👋
            Try @coinseekbot inline bot to start searching for your precious coins.

            Use /help to get some <s>mental</s> help.
        """), parse_mode=ParseMode.HTML)
