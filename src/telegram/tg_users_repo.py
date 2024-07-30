from postgres import PgRepo, pg_session
from .tg_user import TgUser
from sqlalchemy.dialects.postgresql import insert


class TgUsersRepo(PgRepo):
    @pg_session
    async def upsert(self, user: TgUser) -> TgUser:
        query = insert(TgUser).values(user.to_dict())
        query = query.on_conflict_do_update(
            index_elements=[TgUser.tg_id],
            set_=self.on_conflict_do_update_mapping(
                entity=TgUser,
                insert=query,
                conflict=TgUser.tg_id
            )
        ).returning(TgUser)

        raw_hit = await self.session.scalar(query)

        return raw_hit
