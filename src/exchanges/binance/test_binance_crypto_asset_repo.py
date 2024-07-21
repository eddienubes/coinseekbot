import pytest

from container import Container
from exchanges.binance.binance_crypto_asset_repo import BinanceCryptoAssetRepo
from exchanges.binance.entities.binance_crypto_asset import BinanceCryptoAsset


class TestBinanceCryptoAssetRepository:
    @pytest.fixture(autouse=True, scope='session')
    async def repo(self):
        container = Container()
        await container.init()
        repo = container.get(BinanceCryptoAssetRepo)
        yield repo
        await container.destroy()

    async def test_create_assets(self, repo: BinanceCryptoAssetRepo):
        asset = repo.generate()
        await repo.add(asset)

        found_asset = await repo.get(BinanceCryptoAsset, [asset.uuid])

        assert found_asset == asset
