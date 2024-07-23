import pytest
from hamcrest import assert_that, equal_to, has_properties, instance_of, \
    has_items
from asyncpg.pgproto.pgproto import UUID

from container import Container
from .binance_crypto_asset_repo import BinanceCryptoAssetRepo
from .entities.binance_crypto_asset import BinanceCryptoAsset
from postgres.pg_session import pg_session_ctx
from utils import faker


class TestBinanceCryptoAssetRepo:
    @pytest.fixture(autouse=True, scope='class')
    async def repo(self):
        container = Container()
        await container.init()
        repo = container.get(BinanceCryptoAssetRepo)
        yield repo
        await container.destroy()

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

        assert_that(asset, has_properties(
            **found_asset.to_dict(
                uuid=equal_to(asset.uuid)
            )
        ))

    async def test_search_by_ticker(self, repo: BinanceCryptoAssetRepo):
        asset1 = await repo.generate()
        asset2 = await repo.generate()

        tickers = [asset1.ticker, asset2.ticker, faker.pystr(10, 10)]

        result = await repo.search_by_tickers(tickers)

        # noinspection PyTypeChecker
        assert_that(result.hits, has_items(
            has_properties(
                ticker=equal_to(tickers[0])
            ),
            has_properties(
                ticker=equal_to(tickers[1])
            )
        ))

        # noinspection PyTypeChecker
        assert_that(result.misses, has_items(
            equal_to(tickers[2])
        ))

    async def test_insert_asset(self, repo: BinanceCryptoAssetRepo):
        asset = BinanceCryptoAsset(
            uuid=faker.uuid4(),
            name=faker.pystr(3, 10),
            ticker=faker.pystr(3, 10),
            logo_s3_key=faker.image_url()
        )

        inserted_asset = await repo.insert(asset)

        assert_that(inserted_asset, has_properties(
            uuid=instance_of(UUID),
            name=equal_to(asset.name),
            ticker=equal_to(asset.ticker),
            logo_s3_key=equal_to(asset.logo_s3_key)
        ))

    async def test_insert_many_assets(self, repo: BinanceCryptoAssetRepo):
        assets = [
            BinanceCryptoAsset(
                uuid=faker.uuid4(),
                name=faker.pystr(3, 10),
                ticker=faker.pystr(3, 10),
                logo_s3_key=faker.image_url()
            ),
            BinanceCryptoAsset(
                uuid=faker.uuid4(),
                name=faker.pystr(3, 10),
                ticker=faker.pystr(3, 10),
                logo_s3_key=faker.image_url()
            )
        ]

        inserted_assets = await repo.insert_many(assets)

        # noinspection PyTypeChecker
        assert_that(inserted_assets, has_items(
            has_properties(
                uuid=instance_of(UUID),
                name=equal_to(assets[0].name),
                ticker=equal_to(assets[0].ticker),
                logo_s3_key=equal_to(assets[0].logo_s3_key)
            ),
            has_properties(
                uuid=instance_of(UUID),
                name=equal_to(assets[1].name),
                ticker=equal_to(assets[1].ticker),
                logo_s3_key=equal_to(assets[1].logo_s3_key)
            )
        ))
