import pytest

from container import Container
from exchanges.binance import BinanceIngestService


class TestBinanceIngestService:
    @pytest.fixture(autouse=True, scope='class')
    async def service(self):
        container = Container()
        await container.init()
        service = container.get(BinanceIngestService)
        yield service
        await container.destroy()

    # @pytest.mark.skip
    async def test_ingest_assets(self, service: BinanceIngestService):
        await service.ingest_assets()
