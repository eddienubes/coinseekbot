import asyncio

import pytest

from container import Container
from .binance_cron_service import BinanceCronService


class TestBinanceCronService:
    @pytest.fixture(autouse=True, scope='session')
    async def event_loop(self):
        loop = asyncio.get_event_loop_policy().new_event_loop()
        yield loop
        loop.close()

    @pytest.fixture(autouse=True, scope='class')
    async def service(self):
        print('service')
        container = Container()
        await container.init()
        service = container.get(BinanceCronService)
        yield service
        await container.destroy()

    async def test_ingest_assets(self, service: BinanceCronService):
        await service.ingest_assets()
