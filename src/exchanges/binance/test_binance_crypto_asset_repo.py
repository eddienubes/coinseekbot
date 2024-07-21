import asyncio

import pytest

from container import Container
from .binance_crypto_asset_repo import BinanceCryptoAssetRepo
from .entities.binance_crypto_asset import BinanceCryptoAsset
from postgres.pg_session import pg_session_ctx
from utils import faker


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
            asset = await repo.generate()

            await repo.flush()

            found_asset = await repo.get(BinanceCryptoAsset, [asset.uuid])

            assert found_asset == asset

        await pg_session_ctx.run(
            impl
        )

    async def test_create_assets_within_separate_ctx(self, repo: BinanceCryptoAssetRepo):
        asset = await repo.generate()

        # Flush isn't needed here because the transaction is already committed.

        found_asset = await repo.get(BinanceCryptoAsset, [asset.uuid])

        assert found_asset == asset

    async def test_retrieve_non_existent_assets(self, repo: BinanceCryptoAssetRepo):
        asset1 = await repo.generate()
        asset2 = await repo.generate()

        tickers = [asset1.ticker, asset2.ticker, faker.pystr(10, 10)]

        assets = await repo.get_non_existent_tickers(tickers)

        assert len(assets) == 1

        assert assets[0] == tickers[2]
