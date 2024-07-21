from postgres import PgRepo
from utils import faker
from .entities.binance_crypto_asset import BinanceCryptoAsset


class BinanceCryptoAssetRepo(PgRepo):
    def generate(self) -> BinanceCryptoAsset:
        asset = BinanceCryptoAsset(
            name=faker.pystr(3, 10),
            ticker=faker.pystr(3, 10),
            logo_url_s3_key=faker.image_url()
        )
        self.add(asset)

        return asset
