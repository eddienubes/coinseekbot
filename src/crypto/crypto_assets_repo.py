from numpy.random.mtrand import Sequence

from crypto.entities.crypto_asset import CryptoAsset
from crypto.entities.crypto_asset_quote import CryptoAssetQuote
from crypto.entities.crypto_asset_tag import CryptoAssetTag
from crypto.entities.crypto_asset_to_asset_tag import CryptoAssetToAssetTag
from postgres import PgRepo, pg_session

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import MappedColumn, InstrumentedAttribute


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
            print('set: ', set)
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
        print('set: ', assets_set)
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
