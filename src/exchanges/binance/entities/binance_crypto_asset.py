from sqlalchemy import String, UUID, func
from sqlalchemy.orm import mapped_column, Mapped

from postgres.base import Base


class BinanceCryptoAsset(Base):
    __tablename__ = 'binance_crypto_assets'

    uuid: Mapped[str] = mapped_column(UUID, init=False, primary_key=True, server_default=func.gen_random_uuid())
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    ticker: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    logo_url_s3_key: Mapped[str] = mapped_column(String, nullable=False)
