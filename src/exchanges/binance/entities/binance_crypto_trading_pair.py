from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import UUID, func, UniqueConstraint

from postgres.base import Base


class BinanceCryptoTradingPair(Base):
    __tablename__ = 'binance_crypto_trading_pairs'

    uuid: Mapped[UUID] = mapped_column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    base_asset_uuid: Mapped[UUID] = mapped_column(UUID, nullable=False)
    quote_asset_uuid: Mapped[UUID] = mapped_column(UUID, nullable=False)

    __table_args__ = (
        UniqueConstraint('from_asset_uuid', 'to_asset_uuid', name='unique_from_to_asset_pair'),
    )
