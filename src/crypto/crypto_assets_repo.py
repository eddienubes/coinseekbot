from typing import cast

from numpy.random.mtrand import Sequence

from crypto.entities.crypto_asset import CryptoAsset
from crypto.entities.crypto_asset_quote import CryptoAssetQuote
from crypto.entities.crypto_asset_tag import CryptoAssetTag
from crypto.entities.crypto_asset_to_asset_tag import CryptoAssetToAssetTag
from postgres import PgRepo, pg_session

from sqlalchemy import select, func, outerjoin
from sqlalchemy.dialects.postgresql import insert, dialect
from sqlalchemy.orm import MappedColumn, InstrumentedAttribute, aliased, contains_eager
import sqlalchemy as sa


class CryptoAssetsRepo(PgRepo):

    @pg_session
    async def generate(self) -> CryptoAsset:
        asset = CryptoAsset.random()
        tag1 = CryptoAssetTag.random()
        tag2 = CryptoAssetTag.random()

        asset.tags.extend([tag1, tag2])

        await self.add(asset)
        return asset

    @pg_session
    async def find_by_ticker(self, ticker: str) -> CryptoAsset | None:
        query = select(CryptoAsset).where(ticker == CryptoAsset.ticker)

        hit = await self.session.execute(query)
        return hit.scalar()

    @pg_session
    async def bulk_insert(self, assets: list[CryptoAsset]) -> list[CryptoAsset]:
        return await self._insert_many(entity=CryptoAsset, values=assets)

    @pg_session
    async def bulk_upsert(self, values: Sequence[CryptoAsset],
                          conflict: MappedColumn | InstrumentedAttribute = CryptoAsset.uuid
                          ) -> list[CryptoAsset]:

        if not len(values):
            return []

        assets = list[dict]()
        assets_hm = dict[str, list[str]]()
        tags = list[dict]()
        tags_hm = dict[str, CryptoAssetTag]()

        for asset in values:
            assets_hm[asset.ticker] = assets_hm.get(asset.ticker, [])

            for tag in asset.tags:
                if tag.name not in tags_hm:
                    tags_hm[tag.name] = tag
                    tags.append(tag.to_dict())

                assets_hm[asset.ticker].append(tag.name)

            assets.append(asset.to_dict())

        if len(tags):
            set = self.on_conflict_do_update_mapping(CryptoAssetTag, insert(CryptoAssetTag), CryptoAssetTag.name)
            tags_stmt = insert(CryptoAssetTag).values(tags)
            tags_stmt = tags_stmt.on_conflict_do_update(
                index_elements=[CryptoAssetTag.name],
                set_=set
            ).returning(CryptoAssetTag)

            tags = list((await self.session.scalars(tags_stmt)).all())
            print(tags)

        # update tag hash map
        for tag in tags:
            tags_hm[tag.name] = tag

        assets_set = self.on_conflict_do_update_mapping(CryptoAsset, insert(CryptoAsset), conflict)
        
        assets_stmt = insert(CryptoAsset).values(assets)
        assets_stmt = assets_stmt.on_conflict_do_update(
            index_elements=[conflict],
            set_=assets_set
        ).returning(CryptoAsset)

        assets = list((await self.session.scalars(assets_stmt)).all())

        associations = list[dict]()

        for asset in assets:
            for tag_name in assets_hm.get(asset.ticker, []):
                tag_entity = tags_hm[tag_name]

                asset.tags.append(tag_entity)
                associations.append(
                    CryptoAssetToAssetTag(
                        asset_uuid=asset.uuid,
                        tag_uuid=tag_entity.uuid
                    ).to_dict()
                )

        if len(associations):
            associations_stmt = insert(CryptoAssetToAssetTag).values(associations)
            associations_stmt = associations_stmt.on_conflict_do_nothing(
                index_elements=[CryptoAssetToAssetTag.asset_uuid, CryptoAssetToAssetTag.tag_uuid]
            )
            await self.session.execute(associations_stmt)

        return assets

    @pg_session
    async def bulk_insert_quotes(self, quotes: list[CryptoAssetQuote]) -> list[CryptoAssetQuote]:
        return await self._insert_many(entity=CryptoAssetQuote, values=quotes)

    @pg_session
    async def get_with_latest_quote(self, tickers: Sequence[str]) -> list[CryptoAsset]:
        aliased_quote = aliased(CryptoAssetQuote)

        quote_subquery = aliased(select(
            func.row_number().over(
                partition_by=aliased_quote.asset_uuid,
                order_by=aliased_quote.cmc_last_updated.desc()
            ).label('rn'),
            aliased_quote
        ).subquery())

        # to remove duplicate tickers
        asset_subquery = (
            select(
                func.row_number().over(
                    partition_by=CryptoAsset.ticker,
                    order_by=sa.and_(
                        CryptoAsset.num_market_pairs.desc()
                    )
                ).label('rn'),
                quote_subquery,
                CryptoAsset
            )
            .outerjoin(
                target=quote_subquery,
                onclause=sa.and_(quote_subquery.c.rn == 1,
                                 quote_subquery.c.asset_uuid == CryptoAsset.uuid)
            )
            .where(
                sa.and_(
                    quote_subquery.c.id.isnot(None),
                    CryptoAsset.ticker.in_(tickers)
                )
            )
        ).subquery()

        query = (
            select(
                aliased(CryptoAsset, asset_subquery),
                aliased(CryptoAssetQuote, asset_subquery)
            )
            .where(asset_subquery.c.rn == 1)
        )

        raw = (await self.session.execute(query))

        assets = []

        for row in raw.all():
            asset, quote = cast(tuple[CryptoAsset, CryptoAssetQuote], row)

            asset.latest_quote = quote
            assets.append(asset)

        return assets
