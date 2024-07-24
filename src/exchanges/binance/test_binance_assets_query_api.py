import pytest

from container import Container
from exchanges.binance import BinanceAssetsQueryApi


# @pytest.mark.skip
class TestBinanceAssetsQueryApi:
    @pytest.fixture(autouse=True, scope='class')
    async def api(self):
        container = Container()
        await container.init()
        service = container.get(BinanceAssetsQueryApi)
        yield service
        await container.destroy()

    async def test_get_hot_pairs(self, api: BinanceAssetsQueryApi):
        hot_pairs = await api.get_hot_pairs()
        assert hot_pairs is not None

    async def test_get_all_trading_pairs(self, api: BinanceAssetsQueryApi):
        all_pairs = await api.get_all_pairs()
        assert all_pairs is not None

    async def test_get_24h_price_changes(self, api: BinanceAssetsQueryApi):
        price_changes = await api.get_24h_price_changes(symbols=['BTCUSDT'])

        assert price_changes is not None
        assert len(price_changes) == 1
        # assert price_changes is not None
