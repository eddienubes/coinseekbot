import pytest_asyncio

from container import Container
from exchanges.binance.binance_crypto_asset_repo import BinanceCryptoAssetRepo


class TestBinanceCryptoAssetRepository:
    @pytest_asyncio.fixture(autouse=True, scope='class')
    async def service(self):
        container = Container()
        await container.init()
        repo = container.get(BinanceCryptoAssetRepo)
        yield repo
        await container.destroy()
        
    
