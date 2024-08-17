import pytest
import uuid

from container import Container
from crypto.crypto_ingest_service import CryptoIngestService
from crypto.entities.crypto_asset_quote import CryptoAssetQuote


class TestCryptoIngestService:
    @pytest.fixture(autouse=True, scope='class')
    async def service(self, container: Container) -> CryptoIngestService:
        yield container.get(CryptoIngestService)

    async def test_ingest_crypto_assets(self, service: CryptoIngestService):
        await service.ingest_crypto_assets()

    async def test_lock_ingest_crypto_assets(self, service: CryptoIngestService):
        await service.lock_ingest_crypto_assets()

    async def test_hash_quote_changed(self, service: CryptoIngestService):
        quote1 = CryptoAssetQuote.random(asset_uuid=uuid.uuid4())

        assert await service.has_quote_changed(quote1) is True
        assert await service.has_quote_changed(quote1) is False

        quote2 = CryptoAssetQuote.random(**quote1.to_dict())

        assert await service.has_quote_changed(quote2) is False

        quote2.price = 100500

        assert await service.has_quote_changed(quote2) is True
