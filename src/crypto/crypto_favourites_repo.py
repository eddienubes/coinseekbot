from sqlalchemy.dialects.postgresql import insert, UUID
from sqlalchemy.orm import joinedload, contains_eager

from crypto.entities.crypto_asset import CryptoAsset
from crypto.entities.crypto_favourite import CryptoFavourite, CryptoFavouriteStatus
from crypto.entities.crypto_watch import CryptoWatch, CryptoWatchStatus
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
                    CryptoFavourite.status == CryptoFavouriteStatus.ACTIVE
                )
            )
        )

        total = await self.session.scalar(count_query)

        query = (
            sa.select(CryptoFavourite)
            .join(CryptoFavourite.asset)
            .where(
                sa.and_(
                    tg_user_uuid == CryptoFavourite.tg_user_uuid,
                    CryptoFavourite.status == CryptoFavouriteStatus.ACTIVE
                )
            )
            .order_by(
                CryptoFavourite.updated_at.desc()
            )
            .limit(limit)
            .offset(offset)
            # contains_eagers populates the relationship with data from query
            # joinedloads populates the relationship and expands join "on" clause
            .options(
                # https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#contains-eager
                contains_eager(CryptoFavourite.asset),
                joinedload(CryptoFavourite.watch.and_(
                    tg_chat_uuid == CryptoWatch.tg_chat_uuid,
                    CryptoWatchStatus.ACTIVE == CryptoWatch.status
                ))
            )
        )

        hits = await self.session.scalars(query)

        return Pageable(
            hits=list(hits.all()),
            total=total,
            limit=limit,
            offset=offset
        )
