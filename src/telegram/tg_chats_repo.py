from postgres import PgRepo, pg_session
from .tg_chat import TgChat
from sqlalchemy.dialects.postgresql import insert


class TgChatsRepo(PgRepo):
    @pg_session
    async def upsert(self, chat: TgChat) -> TgChat:
        self._logger.info(f'Upserting chat type: {chat.type}')

        chat_dict = chat.to_dict()

        query = insert(TgChat).values(chat_dict)
        query = query.on_conflict_do_update(
            index_elements=[TgChat.tg_id],
            set_=self.on_conflict_do_update_mapping(
                entity=TgChat,
                insert=query,
                conflict=TgChat.tg_id,
                update=list(chat_dict.keys())
            )
        ).returning(TgChat)

        raw_hit = await self.session.scalar(query)

        return raw_hit
