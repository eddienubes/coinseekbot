from datetime import datetime
from decimal import *

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, validates

from postgres import Base
from utils import faker

_PRECISION = 30
_SCALE = 11


class CryptoAssetQuote(Base):
    __tablename__ = 'crypto_asset_quotes'

    id: Mapped[int] = mapped_column(sa.Integer, sa.Identity(), primary_key=True)

    asset_uuid: Mapped[sa.UUID] = mapped_column(
        sa.ForeignKey('crypto_assets.uuid'),
        index=True,
        nullable=False,
        unique=True
    )

    cmc_last_updated: Mapped[datetime] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=False)

    market_cap_dominance: Mapped[Decimal | None] = mapped_column(sa.NUMERIC(precision=_PRECISION, scale=_SCALE),
                                                                 nullable=True)

    percent_change_30d: Mapped[Decimal] = mapped_column(sa.NUMERIC(precision=_PRECISION, scale=_SCALE), nullable=False)
    percent_change_1h: Mapped[Decimal] = mapped_column(sa.NUMERIC(precision=_PRECISION, scale=_SCALE), nullable=False)
    percent_change_24h: Mapped[Decimal] = mapped_column(sa.NUMERIC(precision=_PRECISION, scale=_SCALE), nullable=False)
    percent_change_7d: Mapped[Decimal] = mapped_column(sa.NUMERIC(precision=_PRECISION, scale=_SCALE), nullable=False)
    percent_change_60d: Mapped[Decimal] = mapped_column(sa.NUMERIC(precision=_PRECISION, scale=_SCALE), nullable=False)
    percent_change_90d: Mapped[Decimal] = mapped_column(sa.NUMERIC(precision=_PRECISION, scale=_SCALE), nullable=False)

    market_cap: Mapped[Decimal] = mapped_column(sa.NUMERIC(precision=_PRECISION, scale=_SCALE), nullable=False)

    volume_change_24h: Mapped[Decimal] = mapped_column(sa.NUMERIC(precision=_PRECISION, scale=_SCALE), nullable=False)
    volume_24h: Mapped[Decimal] = mapped_column(sa.NUMERIC(precision=_PRECISION, scale=_SCALE), nullable=False)

    price: Mapped[Decimal] = mapped_column(sa.NUMERIC(precision=_PRECISION, scale=_SCALE), nullable=False)

    @validates(
        'fully_diluted_market_cap',
        'market_cap_dominance',
        'percent_change_30d',
        'percent_change_1h',
        'percent_change_24h',
        'percent_change_7d',
        'percent_change_60d',
        'percent_change_90d',
        'market_cap',
        'volume_change_24h',
        'volume_24h',
        'price'
    )
    def round_precision(self, key: str, value: float) -> float:
        if isinstance(value, float):
            return round(value, _SCALE)

        return value

    @staticmethod
    def random(**kwargs) -> 'CryptoAssetQuote':
        base = CryptoAssetQuote(
            cmc_last_updated=datetime.now().replace(tzinfo=None),
            market_cap_dominance=faker.pydecimal(positive=True, left_digits=5, right_digits=5),
            percent_change_30d=faker.pydecimal(positive=True, left_digits=5, right_digits=5),
            percent_change_1h=faker.pydecimal(positive=True, left_digits=5, right_digits=5),
            percent_change_24h=faker.pydecimal(positive=True, left_digits=5, right_digits=5),
            percent_change_7d=faker.pydecimal(positive=True, left_digits=5, right_digits=5),
            percent_change_60d=faker.pydecimal(positive=True, left_digits=5, right_digits=5),
            percent_change_90d=faker.pydecimal(positive=True, left_digits=5, right_digits=5),
            market_cap=faker.pydecimal(positive=True, left_digits=5, right_digits=5),
            volume_change_24h=faker.pydecimal(positive=True, left_digits=5, right_digits=5),
            volume_24h=faker.pydecimal(positive=True, left_digits=5, right_digits=5),
            price=faker.pydecimal(positive=True, left_digits=5, right_digits=5),
        ).to_dict()

        return CryptoAssetQuote(**{**base, **kwargs})
