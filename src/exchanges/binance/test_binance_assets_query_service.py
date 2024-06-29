import pytest
import pytest_asyncio
from pytest_mock import MockerFixture

from container import Container
from exchanges.binance import BinanceAssetsQueryService
from redis_client import RedisService


class TestBinanceAssetsQueryService:
    @pytest_asyncio.fixture(autouse=True, scope='function')
    async def setup(self, container):
        redis = container.get(RedisService)
        await redis.flush()
        yield

    @pytest_asyncio.fixture(autouse=True, scope='function')
    async def container(self, event_loop):
        container = Container()
        await container.init()
        yield container
        await container.destroy()

    @pytest_asyncio.fixture(autouse=True, scope='function')
    async def service(self, container, event_loop):
        instance = container.get(BinanceAssetsQueryService)
        yield instance

    @pytest.mark.asyncio
    async def test_get_hot_assets_and_cache(self, service):
        assets = await service.get_hot_assets()
        assert len(assets) >= 1

    @pytest.mark.asyncio
    async def test_get_hot_assets_from_cache(self, service, mocker: MockerFixture, container):
        redis = container.get(RedisService)
        redis_spy = mocker.spy(redis, 'set')

        assets = await service.get_hot_assets()
        assert len(assets) >= 1

        assets = await service.get_hot_assets()
        assert len(assets) >= 1

        assert redis_spy.call_count == 1
