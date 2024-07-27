import pytest
from hamcrest import assert_that, has_properties

from container import Container
from crypto.crypto_asset_repo import CryptoAssetRepo
from crypto.entities.crypto_asset import CryptoAsset
from crypto.entities.crypto_asset_quote import CryptoAssetQuote
from crypto.entities.crypto_asset_tag import CryptoAssetTag


class TestCryptoAssetRepo:
    @pytest.fixture(autouse=True, scope='class')
    async def repo(self, container: Container) -> None:
        yield container.get(CryptoAssetRepo)

    async def test_crud(self, repo: CryptoAssetRepo) -> None:
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

    async def test_crud_with_tags_uow(self, repo: CryptoAssetRepo) -> None:
        asset = await repo.generate()

        tags = [CryptoAssetTag.random(), CryptoAssetTag.random()]

        asset.tags.extend(tags)
        await repo.add(asset)

        assert len(asset.tags) == 4

    async def test_crud_with_tags(self, repo: CryptoAssetRepo) -> None:
        asset = await repo.generate()

        tag1 = CryptoAssetTag.random()
        tag2 = CryptoAssetTag.random()

        # tags = await repo.add_all([tag1, tag2])

        asset.tags.extend([tag1, tag2])

        await repo.add(asset)

        # await repo.bulk_insert_tags(asset, )

    async def test_bulk_upsert_relational_data(self, repo: CryptoAssetRepo) -> None:
        tags = [CryptoAssetTag.random() for _ in range(100)]

        assets = [CryptoAsset.random(tags=tags) for _ in range(3)]
        assets = await repo.bulk_upsert(assets, conflict=CryptoAsset.ticker)

        assert len(assets) == 3

    async def test_bulk_insert_quotes(self, repo: CryptoAssetRepo) -> None:
        asset = await repo.generate()

        quotes = [CryptoAssetQuote.random(asset_uuid=asset.uuid) for _ in range(100)]
        await repo.bulk_insert_quotes(quotes)
