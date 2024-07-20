from postgres.repository import Repository
from utils import faker
from .entities.binance_crypto_asset import BinanceCryptoAsset


class BinanceCryptoAssetRepo(Repository):
    def generate(self) -> BinanceCryptoAsset:
        asset = BinanceCryptoAsset(
            name=faker.cryptocurrency_name(),
            ticker=faker.cryptocurrency_code(),
            logo_url_s3_key=faker.image_url()
        )
        self.add(asset)

        return asset
