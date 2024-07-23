from typing import TYPE_CHECKING, Self

from sqlalchemy.orm import mapped_column, Mapped, validates, relationship
from sqlalchemy import UUID, func, UniqueConstraint, String, Boolean, ForeignKey

from postgres.base import Base
from utils import faker
from ..types.binance_trading_pair_status import BinanceTradingPairStatus

if TYPE_CHECKING:
    from .binance_crypto_asset import BinanceCryptoAsset


class BinanceCryptoTradingPair(Base):
    __tablename__ = 'binance_crypto_trading_pairs'

    uuid: Mapped[UUID] = mapped_column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    base_asset_uuid: Mapped[UUID] = mapped_column(ForeignKey('binance_crypto_assets.uuid'), nullable=False)
    # noinspection PyTypeChecker
    base_asset: Mapped['BinanceCryptoAsset'] = relationship(
        back_populates='base_pairs',
        foreign_keys=[base_asset_uuid]
    )

    base_asset_name: Mapped[str] = mapped_column(String, nullable=False)

    @validates('base_asset_name')
    def validate_base_asset_name(self, key, name: str):
        if type(name) is str:
            return name.upper()

    quote_asset_uuid: Mapped[UUID] = mapped_column(ForeignKey('binance_crypto_assets.uuid'), nullable=False)
    # noinspection PyTypeChecker
    quote_asset: Mapped['BinanceCryptoAsset'] = relationship(
        back_populates='quote_pairs',
        foreign_keys=[quote_asset_uuid]
    )
    quote_asset_name: Mapped[str] = mapped_column(String, nullable=False)

    @validates('quote_asset_name')
    def validate_quote_asset_name(self, key, name: str):
        if type(name) is str:
            return name.upper()

    symbol: Mapped[str] = mapped_column(String, nullable=False)

    @validates('symbol')
    def validate_symbol(self, key, symbol: str):
        if type(symbol) is str:
            return symbol.upper()

    status: Mapped[str] = mapped_column(String, nullable=False)
    iceberg_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    oco_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    oto_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    quote_order_qty_market_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    allow_trailing_stop: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    cancel_replace_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_spot_trading_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_margin_trading_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (
        UniqueConstraint('base_asset_uuid', 'quote_asset_uuid', name='unique_from_to_asset_pair'),
    )

    @staticmethod
    def random(base_asset_uuid: UUID, quote_asset_uuid: UUID) -> 'BinanceCryptoTradingPair':
        """Generates a random entity"""
        return BinanceCryptoTradingPair(
            base_asset_uuid=base_asset_uuid,
            base_asset_name=faker.pystr(10, 10),
            quote_asset_uuid=quote_asset_uuid,
            quote_asset_name=faker.pystr(10, 10),
            symbol=faker.pystr(10, 10),
            status=BinanceTradingPairStatus.TRADING.value,
            iceberg_allowed=False,
            oco_allowed=False,
            oto_allowed=True,
            quote_order_qty_market_allowed=True,
            allow_trailing_stop=False,
            cancel_replace_allowed=False,
            is_spot_trading_allowed=False,
            is_margin_trading_allowed=False
        )
