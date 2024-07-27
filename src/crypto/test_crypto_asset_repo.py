import pytest
from hamcrest import assert_that, has_properties

from container import Container
from crypto.crypto_asset_repo import CryptoAssetRepo
from crypto.entities.crypto_asset import CryptoAsset


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
