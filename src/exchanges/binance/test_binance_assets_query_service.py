from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from pytest_mock import MockerFixture

from container import Container
from exchanges.binance import BinanceAssetsQueryService
from redis_client import RedisService


class TestBinanceAssetsQueryService:
    @pytest_asyncio.fixture(autouse=True, scope='function')
    async def setup(self, mocker: MockerFixture):
        container = Container()
        await container.init()

        redis = container.get(RedisService)
        redis_spy = mocker.spy(redis, 'set')

        await redis.flush()

        yield container, redis_spy

        redis_spy.reset_mock()
        await container.destroy()

    @pytest_asyncio.fixture(autouse=True, scope='function')
    async def service(self, setup: tuple[Container]):
        container = setup[0]

        instance = container.get(BinanceAssetsQueryService)
        yield instance

    class TestGetAllAssetsAndCache:
        @pytest.mark.asyncio
        async def test_get_all_assets_and_cache(self, service: BinanceAssetsQueryService):
            assets = await service.get_all_assets()
            assert len(assets) >= 1

        @pytest.mark.asyncio
        async def test_get_all_assets_from_cache(self, service: BinanceAssetsQueryService,
                                                 setup: [Container, AsyncMock]):
            _, redis_spy = setup

            assets = await service.get_all_assets()
            assert len(assets) >= 1

            assets = await service.get_all_assets()
            assert len(assets) >= 1

            assert redis_spy.call_count == 1

    class TestGetHotPairsAndCache:
        @pytest.mark.asyncio
        async def test_get_hot_pairs_and_cache(self, service):
            pairs = await service.get_hot_pairs()
            assert len(pairs) >= 1

        @pytest.mark.asyncio
        async def test_get_hot_pairs_from_cache(self, service, setup: [Container, AsyncMock]):
            _, redis_spy = setup

            pairs = await service.get_hot_pairs()
            assert len(pairs) >= 1

            pairs = await service.get_hot_pairs()
            assert len(pairs) >= 1

            assert redis_spy.call_count == 1
