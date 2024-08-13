from sqlalchemy.dialects.postgresql import insert, UUID
from crypto.entities.crypto_favourite import CryptoFavourite
from crypto.entities.crypto_watch import CryptoWatch
from postgres import PgRepo, pg_session
import sqlalchemy as sa

from utils import Pageable


class CryptoFavouritesRepo(PgRepo):
    @pg_session
    async def upsert(self, relation: CryptoFavourite) -> None:
        relation_dict = relation.to_dict()

        query = insert(CryptoFavourite).values(relation_dict)
        query = query.on_conflict_do_update(
            index_elements=[CryptoFavourite.asset_uuid, CryptoFavourite.tg_user_uuid],
            set_=self.on_conflict_do_update_mapping(
                entity=CryptoFavourite,
                insert=query,
                conflict=[CryptoFavourite.asset_uuid, CryptoFavourite.tg_user_uuid]
            )
        ).returning(CryptoFavourite)

        await self.session.scalar(query)

    @pg_session
    async def get_by_tg_user_uuid_with_assets(
            self,
            tg_user_uuid: UUID | str,
            tg_chat_uuid: UUID | str,
            limit: int = 5,
            offset: int = 0
    ) -> Pageable[CryptoFavourite]:
        count_query = (
            sa.select(sa.func.count(CryptoFavourite.uuid))
            .where(
                sa.and_(
                    tg_user_uuid == CryptoFavourite.tg_user_uuid,
                    CryptoFavourite.deleted_at.is_(None)
                )
            )
        )

        total = await self.session.scalar(count_query)

        query = (
            sa.select(CryptoFavourite)
            .join(CryptoFavourite.asset)
            .outerjoin(
                CryptoFavourite.watch,
                tg_chat_uuid == CryptoWatch.tg_chat_uuid
            )
            .where(
                sa.and_(
                    tg_user_uuid == CryptoFavourite.tg_user_uuid,
                    CryptoFavourite.deleted_at.is_(None)
                )
            )
            .order_by(CryptoFavourite.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )

        hits = await self.session.scalars(query)

        return Pageable(
            hits=list(hits.all()),
            total=total,
            limit=limit,
            offset=offset
        )
