from tokenize import String
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column, validates


class BinanceCryptoAssetV2:
    __tablename__ = 'binance_crypto_assets'

    uuid: Mapped[UUID] = mapped_column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    name: Mapped[str] = mapped_column(String, unique=False, nullable=False)

    @validates('name')
    def validate_name(self, key, name: str):
        if type(name) is str:
            return name.upper()

    ticker: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    @validates('ticker')
    def validate_ticker(self, key, ticker: str):
        if type(ticker) is str:
            return ticker.upper()

    logo_s3_key: Mapped[str] = mapped_column(String, nullable=False)

    # Sequence number for the asset. Not sure what this is, but I think it represents the asset priority.
    # Userful for ordering assets
    seq_num: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    base_pairs: Mapped[list['BinanceCryptoTradingPair']] = relationship(
        'BinanceCryptoTradingPair',
        back_populates='base_asset',
        primaryjoin='BinanceCryptoAsset.uuid == BinanceCryptoTradingPair.base_asset_uuid',
        foreign_keys='BinanceCryptoTradingPair.base_asset_uuid'
    )

    quote_pairs: Mapped[list['BinanceCryptoTradingPair']] = relationship(
        'BinanceCryptoTradingPair',
        back_populates='quote_asset',
        primaryjoin='BinanceCryptoAsset.uuid == BinanceCryptoTradingPair.quote_asset_uuid',
        foreign_keys='BinanceCryptoTradingPair.quote_asset_uuid'
    )

    @staticmethod
    def random(ticker: str = faker.pystr(10, 10)) -> 'BinanceCryptoAsset':
        return BinanceCryptoAsset(
            name=faker.pystr(3, 10),
            ticker=ticker,
            seq_num=faker.pyint(1, 100),
            logo_s3_key=faker.image_url()
        )
