import uuid
from typing import cast

from numpy.random.mtrand import Sequence

from utils import Pageable
from .entities.crypto_asset import CryptoAsset
from .entities.crypto_asset_quote import CryptoAssetQuote
from .entities.crypto_asset_tag import CryptoAssetTag
from postgres import PgRepo, pg_session

from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import MappedColumn, InstrumentedAttribute, aliased
import sqlalchemy as sa

from .entities.crypto_asset_to_asset_tag import CryptoAssetToAssetTag


class CryptoAssetsRepo(PgRepo):
    @pg_session
    async def get_by_cmc_ids(self, cmc_ids: Sequence[int]) -> list[CryptoAsset]:
        query = select(CryptoAsset).where(CryptoAsset.cmc_id.in_(cmc_ids))

        hit = await self.session.scalars(query)
        return list(hit.all())

    @pg_session
    async def generate(self, **kwargs) -> CryptoAsset:
        asset = CryptoAsset.random(**kwargs)
        tag1 = CryptoAssetTag.random()
        tag2 = CryptoAssetTag.random()

        asset.tags.extend([tag1, tag2])

        await self.add(asset)
        return asset

    @pg_session
    async def get_by_uuid(self, uuid: str) -> CryptoAsset | None:
        query = select(CryptoAsset).where(uuid == CryptoAsset.uuid)

        hit = await self.session.execute(query)
        return hit.scalar()

    @pg_session
    async def try_get_by_uuid(self, uuid: str) -> CryptoAsset:
        query = select(CryptoAsset).where(uuid == CryptoAsset.uuid)

        hit = await self.session.execute(query)
        hit = hit.scalar()

        if hit is None:
            raise ValueError(f'Asset with uuid {uuid} not found')

        return hit

    @pg_session
    async def get_by_ticker(self, ticker: str) -> CryptoAsset | None:
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
            assets.append(asset.to_dict())
            assets_hm[asset.ticker] = assets_hm.get(asset.ticker, [])

            for tag in asset.tags:
                if tag.name not in tags_hm:
                    tags_hm[tag.name] = tag
                    tags.append(tag.to_dict())

                assets_hm[asset.ticker].append(tag.name)

        if len(tags):
            tags_stmt = insert(CryptoAssetTag).values(tags)
            tags_stmt = tags_stmt.on_conflict_do_update(
                index_elements=[CryptoAssetTag.name],
                set_=self.on_conflict_do_update_mapping(CryptoAssetTag, tags_stmt, CryptoAssetTag.name)
            ).returning(CryptoAssetTag)

            tags = list((await self.session.scalars(tags_stmt)).all())

        # update tag hash map
        for tag in tags:
            tags_hm[tag.name] = tag

        assets_stmt = insert(CryptoAsset).values(assets)
        assets_stmt = assets_stmt.on_conflict_do_update(
            index_elements=[conflict],
            set_=self.on_conflict_do_update_mapping(CryptoAsset, assets_stmt, conflict)
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
    async def bulk_upsert_quotes(self, quotes: list[CryptoAssetQuote]) -> list[CryptoAssetQuote]:
        if not quotes:
            return []

        quotes_dicts = [watch.to_dict() for watch in quotes]

        query = insert(CryptoAssetQuote).values(quotes_dicts)
        query = query.on_conflict_do_update(
            index_elements=[CryptoAssetQuote.asset_uuid],
            set_=self.on_conflict_do_update_mapping(
                entity=CryptoAssetQuote,
                insert=query,
                conflict=[CryptoAssetQuote.asset_uuid],
                update=list(quotes_dicts[0].keys())
            )
        ).returning(CryptoAssetQuote)

        raw_hits = await self.session.scalars(query)

        return list(raw_hits.all())

    @pg_session
    async def get_with_latest_quote(
            self,
            tickers: Sequence[str],
            dedupe: bool = True,
            fuzzy: bool = False,
            limit=50
    ) -> list[CryptoAsset]:
        """
        Get assets with latest quote
        :param limit:
        :param fuzzy: Enable fuzzy search. Just ilike for now.
        :param tickers: The list of tickers to look for
        :param dedupe: Deduplicates assets by tickers and leaves only the ones with the most market pairs.
        Otherwise, it will return matching assets sorted by most market pairs.
        :return:
        """

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
                    # *[
                    #     CryptoAsset.ticker.in_(tickers)
                    # ]

                    sa.or_(
                        *[CryptoAsset.ticker.ilike(f'%{ticker}%') for ticker in tickers],
                        *[CryptoAsset.name.ilike(f'%{ticker}%') for ticker in tickers]
                    ) if fuzzy else
                    CryptoAsset.ticker.in_(tickers)
                )
            )
        ).subquery()

        query = select(
            aliased(CryptoAsset, asset_subquery),
            aliased(CryptoAssetQuote, asset_subquery)
        )

        if dedupe:
            query = query.where(asset_subquery.c.rn == 1)
        else:
            query = query.order_by(asset_subquery.c.market_cap.desc())

        query = query.limit(limit)

        raw = (await self.session.execute(query))

        assets = []

        for row in raw.all():
            asset, quote = cast(tuple[CryptoAsset, CryptoAssetQuote], row)

            asset.latest_quote = quote
            assets.append(asset)

        return assets
