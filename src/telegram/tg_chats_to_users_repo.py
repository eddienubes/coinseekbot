from postgres import PgRepo, pg_session
from sqlalchemy.dialects.postgresql import insert

from .tg_chat_to_user import TgChatToUser


class TgChatsToUsersRepo(PgRepo):
    @pg_session
    async def upsert(self, relation: TgChatToUser) -> None:
        query = insert(TgChatToUser).values(relation.to_dict())
        query = query.on_conflict_do_nothing(
            index_elements=[TgChatToUser.chat_uuid, TgChatToUser.user_uuid],
        ).returning(TgChatToUser)

        await self.session.scalar(query)
