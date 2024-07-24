import pytest
from hamcrest import assert_that, equal_to, has_properties, instance_of, \
    has_items
from asyncpg.pgproto.pgproto import UUID

from container import Container
from . import BinanceCryptoTradingPairsRepo, BinanceCryptoTradingPair, BinanceCryptoAssetRepo
from postgres.pg_session import pg_session_ctx


class TestBinanceCryptoTradingPairsRepo:
    @pytest.fixture(autouse=True, scope='class')
    async def container(self):
        container = Container()
        await container.init()
        yield container
        await container.destroy()

    @pytest.fixture(autouse=True, scope='class')
    async def repo(self, container: Container):
        repo = container.get(BinanceCryptoTradingPairsRepo)
        yield repo

    async def test_create_pairs_within_single_ctx(self, repo: BinanceCryptoTradingPairsRepo, container: Container):
        binance_crypto_asset_repo = container.get(BinanceCryptoAssetRepo)

        async def impl():
            base_asset = await binance_crypto_asset_repo.generate()
            quote_asset = await binance_crypto_asset_repo.generate()

            await binance_crypto_asset_repo.flush()

            pair = await repo.generate(base_asset.uuid, quote_asset.uuid)

            await repo.flush()

            found_asset = await repo.get(BinanceCryptoTradingPair, [pair.uuid])

            assert found_asset == pair

        await pg_session_ctx.run(
            impl
        )

    # async def test_search_by_ticker(self, repo: BinanceCryptoTradingPairsRepo):
    #     asset1 = await repo.generate()
    #     asset2 = await repo.generate()
    # 
    #     tickers = [asset1.ticker, asset2.ticker, faker.pystr(10, 10)]
    # 
    #     result = await repo.search_by_tickers(tickers)
    # 
    #     # noinspection PyTypeChecker
    #     assert_that(result.hits, has_items(
    #         has_properties(
    #             ticker=equal_to(tickers[0])
    #         ),
    #         has_properties(
    #             ticker=equal_to(tickers[1])
    #         )
    #     ))
    # 
    #     # noinspection PyTypeChecker
    #     assert_that(result.misses, has_items(
    #         equal_to(tickers[2])
    #     ))

    async def test_insert_pair(self, repo: BinanceCryptoTradingPairsRepo, container: Container):
        binance_crypto_asset_repo = container.get(BinanceCryptoAssetRepo)

        base_asset = await binance_crypto_asset_repo.generate()
        quote_asset = await binance_crypto_asset_repo.generate()

        asset = BinanceCryptoTradingPair.random(base_asset.uuid, quote_asset.uuid)

        inserted_asset = await repo.insert(asset)

        assert_that(inserted_asset, has_properties(
            uuid=instance_of(UUID),
            base_asset_uuid=equal_to(base_asset.uuid),
            quote_asset_uuid=equal_to(quote_asset.uuid),
        ))

    async def test_insert_many_pairs(self, repo: BinanceCryptoTradingPairsRepo, container: Container):
        binance_crypto_asset_repo = container.get(BinanceCryptoAssetRepo)

        base_asset = await binance_crypto_asset_repo.generate()
        quote_asset = await binance_crypto_asset_repo.generate()

        assets = [
            BinanceCryptoTradingPair.random(base_asset.uuid, quote_asset.uuid),
            BinanceCryptoTradingPair.random(quote_asset.uuid, base_asset.uuid)
        ]

        inserted_assets = await repo.insert_many(assets)

        # noinspection PyTypeChecker
        assert_that(inserted_assets, has_items(
            has_properties(
                uuid=instance_of(UUID),
                base_asset_uuid=equal_to(base_asset.uuid),
                quote_asset_uuid=equal_to(quote_asset.uuid),
            ),
            has_properties(
                uuid=instance_of(UUID),
                base_asset_uuid=equal_to(quote_asset.uuid),
                quote_asset_uuid=equal_to(base_asset.uuid),
            )
        ))

    async def test_get_all(self, repo: BinanceCryptoTradingPairsRepo, container: Container):
        binance_crypto_asset_repo = container.get(BinanceCryptoAssetRepo)

        base_asset = await binance_crypto_asset_repo.generate()
        quote_asset = await binance_crypto_asset_repo.generate()

        existing_pair = await repo.generate(base_asset.uuid, quote_asset.uuid)

        pair = await repo.get_all()

        # noinspection PyTypeChecker
        assert_that(pair, has_items(
            has_properties(
                uuid=equal_to(existing_pair.uuid)
            )
        ))
