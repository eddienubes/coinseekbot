import pytest

from container import Container
from exchanges.binance import BinanceTradingPairsService, BinanceIngestService


class TestBinanceTradingPairsService:
    @pytest.fixture(autouse=True, scope='class')
    async def service(self, container: Container):
        service = container.get(BinanceTradingPairsService)
        yield service

    async def test_update_pair_price_changes(self, service: BinanceTradingPairsService, container: Container):
        ingest_service = container.get(BinanceIngestService)
        await ingest_service.ingest_assets()

        await service.update_trading_pair_price_changes()
