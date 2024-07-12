from sqlalchemy.orm import Session

from exchanges.binance.entities.binance_crypto_asset import BinanceCryptoAsset


class BinanceCryptoAssetRepository:
    def __init__(self, session: Session):
        self.__session = session

    async def create(self) -> BinanceCryptoAsset:
        asset = BinanceCryptoAsset()
        self.__session.add(asset)
        return asset

    async def findbyid_if_any(self, asset_uuid: str) -> BinanceCryptoAsset | None:
        result = self.__session.query(BinanceCryptoAsset).where(BinanceCryptoAsset.uuid == asset_uuid).first()
        return result
