import pytest

from container import Container
from exchanges.binance.clients.binance_ui_api import BinanceUiApi


class TestBinanceUiApi:
    @pytest.fixture(autouse=True, scope='class')
    async def api(self, container: Container):
        yield container.get(BinanceUiApi)

    async def test_get_all_coins(self, api: BinanceUiApi):
        res = await api.get_all_coins(limit=5)

        assert len(res.data) == 5
        assert res.status.total_count > 10000
