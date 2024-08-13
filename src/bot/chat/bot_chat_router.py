from aiogram.enums import ParseMode
from aiogram.types import ChatMemberUpdated

from bot import TelegramBot
from aiogram.filters import ChatMemberUpdatedFilter, LEAVE_TRANSITION, JOIN_TRANSITION

from bot.constants import SHIT_MEME_STICKER_ID
from telegram.entities.tg_chat import TgChat
from telegram.tg_chats_repo import TgChatsRepo
from .views import render_join


@TelegramBot.router()
class BotChatRouter:
    def __init__(self,
                 chats_repo: TgChatsRepo
                 ):
        self.__chats_repo = chats_repo

    @TelegramBot.handle_my_chat_member(ChatMemberUpdatedFilter(LEAVE_TRANSITION))
    async def remove(self, message: ChatMemberUpdated):
        await self.handle_join_or_removal(message, removed=True)

    @TelegramBot.handle_my_chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
    async def join(self, message: ChatMemberUpdated):
        await self.handle_join_or_removal(message, removed=False)
        await message.answer_sticker(sticker=SHIT_MEME_STICKER_ID)
        await message.answer(render_join(), parse_mode=ParseMode.HTML)

    async def handle_join_or_removal(self, message: ChatMemberUpdated, removed: bool) -> None:
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
                invite_link=message.chat.invite_link,
                is_removed=removed
            )
        )
