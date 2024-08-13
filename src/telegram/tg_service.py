import logging

from aiogram.types import Update

from postgres import pg_session
from telegram.entities.tg_chat import TgChat
from telegram.entities.tg_chat_to_user import TgChatToUser
from .tg_chats_repo import TgChatsRepo
from .tg_chats_to_users_repo import TgChatsToUsersRepo
from telegram.entities.tg_user import TgUser
from .tg_users_repo import TgUsersRepo


class TgService:
    def __init__(self,
                 tg_users_repo: TgUsersRepo,
                 tg_chats_repo: TgChatsRepo,
                 tg_chats_to_users_repo: TgChatsToUsersRepo
                 ):
        self.__tg_user_repo = tg_users_repo
        self.__tg_chats_repo = tg_chats_repo
        self.__tg_chats_to_users_repo = tg_chats_to_users_repo
        self.__logger = logging.getLogger(self.__class__.__name__)

    @pg_session
    async def upsert_user_in_chat_from_update(self, update: Update) -> (TgChat | None, TgUser | None):
        self.__logger.info('Upserting user in chat from update')

        event = update.event

        event_chat = getattr(event, 'chat', None)
        chat = None
        user = None

        if event_chat:
            chat = TgChat(
                tg_id=event_chat.id,
                type=event_chat.type,
                username=event_chat.username,
                fullname=event_chat.full_name,
                is_forum=event_chat.is_forum,
                description=event_chat.description,
                bio=event_chat.bio,
                join_by_request=event_chat.join_by_request,
                invite_link=event_chat.invite_link
            )

            chat = await self.__tg_chats_repo.upsert(chat)

        event_user = getattr(event, 'from_user', None)

        if event_user:
            user = TgUser(
                tg_id=event_user.id,
                is_bot=event_user.is_bot,
                first_name=event_user.first_name,
                last_name=event_user.last_name,
                username=event_user.username,
                language_code=event_user.language_code,
                is_premium=event_user.is_premium,
                added_to_attachment_menu=event_user.added_to_attachment_menu
            )

            user = await self.__tg_user_repo.upsert(user)

        if chat and user:
            relation = TgChatToUser(
                chat_uuid=chat.uuid,
                user_uuid=user.uuid
            )

            await self.__tg_chats_to_users_repo.upsert(relation)

        return chat, user
