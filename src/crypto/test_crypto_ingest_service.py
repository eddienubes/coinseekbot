import pytest

from container import Container
from crypto.crypto_ingest_service import CryptoIngestService


class TestCryptoIngestService:
    @pytest.fixture(autouse=True, scope='class')
    async def service(self, container: Container) -> CryptoIngestService:
        yield container.get(CryptoIngestService)

    async def test_ingest_crypto_assets(self, service: CryptoIngestService):
        await service.ingest_crypto_assets()

    async def test_lock_ingest_crypto_assets(self, service: CryptoIngestService):
        await service.lock_ingest_crypto_assets()
