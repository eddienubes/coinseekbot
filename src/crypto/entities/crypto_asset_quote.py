from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, validates

from postgres import Base
from utils import faker


class CryptoAssetQuote(Base):
    __tablename__ = 'crypto_asset_quotes'

    id: Mapped[int] = mapped_column(sa.Integer, sa.Identity(), primary_key=True)

    asset_uuid: Mapped[sa.UUID] = mapped_column(sa.ForeignKey('crypto_assets.uuid'), index=True, nullable=False)

    cmc_last_updated: Mapped[datetime] = mapped_column(sa.TIMESTAMP, nullable=False)

    market_cap_dominance: Mapped[float] = mapped_column(sa.NUMERIC(precision=30, scale=4), nullable=False)

    percent_change_30d: Mapped[float] = mapped_column(sa.NUMERIC(precision=30, scale=4), nullable=False)
    percent_change_1h: Mapped[float] = mapped_column(sa.NUMERIC(precision=30, scale=4), nullable=False)
    percent_change_24h: Mapped[float] = mapped_column(sa.NUMERIC(precision=30, scale=4), nullable=False)
    percent_change_7d: Mapped[float] = mapped_column(sa.NUMERIC(precision=30, scale=4), nullable=False)
    percent_change_60d: Mapped[float] = mapped_column(sa.NUMERIC(precision=30, scale=4), nullable=False)
    percent_change_90d: Mapped[float] = mapped_column(sa.NUMERIC(precision=30, scale=4), nullable=False)

    market_cap: Mapped[float] = mapped_column(sa.NUMERIC(precision=30, scale=4), nullable=False)

    volume_change_24h: Mapped[float] = mapped_column(sa.NUMERIC(precision=30, scale=4), nullable=False)
    volume_24h: Mapped[float] = mapped_column(sa.NUMERIC(precision=30, scale=4), nullable=False)

    price: Mapped[float] = mapped_column(sa.NUMERIC(precision=30, scale=4), nullable=False)

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
            return round(value, 4)

        return value

    @staticmethod
    def random(asset_uuid: sa.UUID) -> 'CryptoAssetQuote':
        return CryptoAssetQuote(
            asset_uuid=asset_uuid,
            cmc_last_updated=datetime.now(),
            market_cap_dominance=faker.pyfloat(positive=True),
            percent_change_30d=faker.pyfloat(positive=True),
            percent_change_1h=faker.pyfloat(positive=True),
            percent_change_24h=faker.pyfloat(positive=True),
            percent_change_7d=faker.pyfloat(positive=True),
            percent_change_60d=faker.pyfloat(positive=True),
            percent_change_90d=faker.pyfloat(positive=True),
            market_cap=faker.pyfloat(positive=True),
            volume_change_24h=faker.pyfloat(positive=True),
            volume_24h=faker.pyfloat(positive=True),
            price=faker.pyfloat(positive=True),
        )
