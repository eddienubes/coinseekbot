from sqlalchemy import String, UUID
from sqlalchemy.orm import mapped_column, Mapped

from postgres import Base


class BinanceCryptoAsset(Base):
    __tablename__ = 'binance_crypto_assets'

    uuid = mapped_column(UUID, primary_key=True)
    name = mapped_column(String, unique=True, nullable=False)
    ticker = mapped_column(String, unique=True, nullable=False)
    logo_url_s3_key = mapped_column(String, nullable=False)
