import logging

from aiogram.types import Update

from postgres import pg_session
from .tg_chat import TgChat
from .tg_chat_to_user import TgChatToUser
from .tg_chats_repo import TgChatsRepo
from .tg_chats_to_users_repo import TgChatsToUsersRepo
from .tg_user import TgUser
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
    async def upsert_user_in_chat_from_update(self, update: Update):
        self.__logger.info('Upserting user in chat from update')

        event = update.event

        chat = TgChat(
            tg_id=event.chat.id,
            type=event.chat.type,
            username=event.chat.username,
            fullname=event.chat.full_name,
            is_forum=event.chat.is_forum,
            description=event.chat.description,
            bio=event.chat.bio,
            join_by_request=event.chat.join_by_request,
            invite_link=event.chat.invite_link
        )

        chat = await self.__tg_chats_repo.upsert(chat)

        event_user = event.from_user

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

            relation = TgChatToUser(
                chat_uuid=chat.uuid,
                user_uuid=user.uuid
            )

            await self.__tg_chats_to_users_repo.upsert(relation)
