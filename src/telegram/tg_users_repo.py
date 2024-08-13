from uuid import UUID

from postgres import PgRepo, pg_session
from telegram.entities.tg_chat import TgChat
from telegram.entities.tg_user import TgUser
from sqlalchemy.dialects.postgresql import insert
import sqlalchemy as sa


class TgUsersRepo(PgRepo):
    @pg_session
    async def get_by_tg_id_with_chat(
            self,
            tg_user_id: int,
            tg_chat_id: int
    ) -> TgUser | None:
        query = (
            sa.select(TgUser)
            .outerjoin(TgChat, TgChat.tg_id == tg_chat_id)
            .where(
                sa.and_(
                    tg_user_id == TgUser.tg_id
                )
            )
        )

        raw_hit = await self.session.scalar(query)

        return raw_hit

    @pg_session
    async def try_get_by_tg_id(self, tg_id: int) -> TgUser:
        user = await self.get_by_tg_id(tg_id)

        if user is None:
            raise ValueError(f'TgUser with tg_id={tg_id} not found')

        return user

    @pg_session
    async def get_by_tg_id(self, tg_id: int) -> TgUser | None:
        query = sa.select(
            TgUser
        ).where(
            tg_id == TgUser.tg_id
        )

        raw_hit = await self.session.scalar(query)

        return raw_hit

    @pg_session
    async def upsert(self, user: TgUser) -> TgUser:
        user_dict = user.to_dict()
        keys = list(user_dict.keys())

        query = insert(TgUser).values(user_dict)
        query = query.on_conflict_do_update(
            index_elements=[TgUser.tg_id],
            set_=self.on_conflict_do_update_mapping(
                entity=TgUser,
                insert=query,
                conflict=TgUser.tg_id,
                update=keys
            )
        ).returning(TgUser)

        raw_hit = await self.session.scalar(query)

        return raw_hit
