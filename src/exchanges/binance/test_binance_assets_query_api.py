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
