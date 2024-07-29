import pytest
from hamcrest import assert_that, has_properties, has_items

from container import Container
from crypto.crypto_assets_repo import CryptoAssetsRepo
from crypto.entities.crypto_asset import CryptoAsset
from crypto.entities.crypto_asset_quote import CryptoAssetQuote
from crypto.entities.crypto_asset_tag import CryptoAssetTag


class TestCryptoAssetRepo:
    @pytest.fixture(autouse=True, scope='class')
    async def repo(self, container: Container) -> None:
        yield container.get(CryptoAssetsRepo)

    async def test_crud(self, repo: CryptoAssetsRepo) -> None:
        asset = await repo.generate()
        assert asset

        found = await repo.find_by_ticker(asset.ticker)

        assert found.uuid == asset.uuid

        assert_that(found, has_properties(
            ticker=asset.ticker,
            name=asset.name,
        ))

        new_name = 'new name'
        found.name = new_name

        upserted_assets = await repo.bulk_upsert([found], conflict=CryptoAsset.ticker)

        assert upserted_assets[0].name == new_name

    async def test_crud_with_tags_uow(self, repo: CryptoAssetsRepo) -> None:
        asset = await repo.generate()

        tags = [CryptoAssetTag.random(), CryptoAssetTag.random()]

        asset.tags.extend(tags)
        await repo.add(asset)

        assert len(asset.tags) == 4

    async def test_crud_with_tags(self, repo: CryptoAssetsRepo) -> None:
        asset = await repo.generate()

        tag1 = CryptoAssetTag.random()
        tag2 = CryptoAssetTag.random()

        # tags = await repo.add_all([tag1, tag2])

        asset.tags.extend([tag1, tag2])

        await repo.add(asset)

        # await repo.bulk_insert_tags(asset, )

    async def test_bulk_upsert_relational_data(self, repo: CryptoAssetsRepo) -> None:
        tags = [CryptoAssetTag.random() for _ in range(100)]

        assets = [CryptoAsset.random(tags=tags) for _ in range(3)]
        assets = await repo.bulk_upsert(assets, conflict=CryptoAsset.ticker)

        assets = await repo.bulk_upsert(assets, conflict=CryptoAsset.ticker)

        assert len(assets) == 3

    async def test_bulk_insert_quotes(self, repo: CryptoAssetsRepo) -> None:
        asset = await repo.generate()

        quotes = [CryptoAssetQuote.random(asset_uuid=asset.uuid) for _ in range(100)]
        await repo.bulk_insert_quotes(quotes)

    async def test_get_with_latest_quote(self, repo: CryptoAssetsRepo) -> None:
        asset1 = await repo.generate()
        asset2 = await repo.generate()
        quote1 = CryptoAssetQuote.random(asset_uuid=asset1.uuid)
        quote2 = CryptoAssetQuote.random(asset_uuid=asset2.uuid)

        quote1 = await repo.add(quote1)
        quote2 = await repo.add(quote2)

        assets = await repo.get_with_latest_quote([asset1.ticker, asset2.ticker])

        # noinspection PyTypeChecker
        assert_that(assets, has_items(
            has_properties(
                ticker=asset1.ticker,
                name=asset1.name,
                latest_quote=has_properties(
                    id=quote1.id,
                    price=quote1.price,
                    # volume_24h=quote1.volume_24h,
                    # last_updated=quote1.cmc_last_updated
                )
            ),
            has_properties(
                ticker=asset2.ticker,
                name=asset2.name,
                # latest_quote=has_properties(
                #     id=quote2.id,
                #     price=quote2.price,
                #     volume_24h=quote2.volume_24h,
                #     last_updated=quote2.cmc_last_updated
                # )
            )
        ))
