import asyncio

import pytest

from container import Container
from .binance_cron_service import BinanceCronService


class TestBinanceCronService:
    @pytest.fixture(autouse=True, scope='class')
    async def service(self):
        container = Container()
        await container.init()
        service = container.get(BinanceCronService)
        yield service
        await container.destroy()

    async def test_ingest_assets(self, service: BinanceCronService):
        await service.ingest_assets()
