import asyncio
import pytest

from container import Container
from exchanges.binance.binance_crypto_asset_repo import BinanceCryptoAssetRepo
from exchanges.binance.entities.binance_crypto_asset import BinanceCryptoAsset
from postgres.pg_session import pg_session_ctx


class TestBinanceCryptoAssetRepository:
    @pytest.fixture(autouse=True, scope='session')
    async def event_loop(self):
        loop = asyncio.get_event_loop_policy().new_event_loop()
        yield loop
        loop.close()

    @pytest.fixture(autouse=True, scope='class')
    async def repo(self):
        container = Container()
        await container.init()
        repo = container.get(BinanceCryptoAssetRepo)
        yield repo
        await container.destroy()

    @pytest.mark.asyncio
    async def test_create_assets_within_single_ctx(self, repo: BinanceCryptoAssetRepo):
        async def impl():
            asset = repo.generate()
            await repo.add(asset)

            await repo.flush()

            found_asset = await repo.get(BinanceCryptoAsset, [asset.uuid])

            assert found_asset == asset

        await pg_session_ctx.run(
            impl
        )

    async def test_create_assets_within_separate_ctx(self, repo: BinanceCryptoAssetRepo):
        asset = repo.generate()
        await repo.add(asset)

        # Flush isn't needed here because the transaction is already committed.

        found_asset = await repo.get(BinanceCryptoAsset, [asset.uuid])

        assert found_asset == asset
