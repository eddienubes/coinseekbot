from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import mapped_column, Mapped, relationship
import sqlalchemy as sa

from postgres import Base
from utils import faker
from .crypto_asset_to_asset_tag import CryptoAssetToAssetTag

if TYPE_CHECKING:
    from .crypto_asset_tag import CryptoAssetTag
    from .crypto_asset_quote import CryptoAssetQuote


class CryptoAsset(Base):
    __tablename__ = 'crypto_assets'

    uuid: Mapped[sa.UUID] = mapped_column(sa.UUID, primary_key=True, server_default=sa.func.gen_random_uuid())
    ticker: Mapped[str] = mapped_column(sa.String, unique=False, nullable=False, index=True)

    name: Mapped[str] = mapped_column(sa.String, unique=False, nullable=False, index=True)
    slug: Mapped[str] = mapped_column(sa.String, unique=False, nullable=False, index=True)

    cmc_date_added: Mapped[datetime] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=False)
    num_market_pairs: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    infinite_supply: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=False)
    max_supply: Mapped[str | None] = mapped_column(sa.String, nullable=True)

    cmc_id: Mapped[int] = mapped_column(sa.Integer, unique=True, nullable=False)

    @property
    def small_logo_url(self) -> str:
        return f'https://s2.coinmarketcap.com/static/img/coins/64x64/{self.cmc_id}.png'

    @property
    def large_logo_url(self) -> str:
        return f'https://s2.coinmarketcap.com/static/img/coins/128x128/{self.cmc_id}.png'

    tags: Mapped[list['CryptoAssetTag']] = relationship(
        secondary=CryptoAssetToAssetTag.__table__,
        back_populates='assets',
        lazy='noload',
        viewonly=True
    )

    latest_quote: Mapped['CryptoAssetQuote'] = relationship(
        'CryptoAssetQuote',
        lazy='noload',
        viewonly=True
    )

    @staticmethod
    def random(**kwargs) -> 'CryptoAsset':
        base_entity = CryptoAsset(
            ticker=faker.pystr(10, 10),
            name=faker.pystr(10, 10),
            slug=faker.pystr(10, 10),
            cmc_date_added=datetime.now(),
            num_market_pairs=faker.pyint(1, 100),
            infinite_supply=False,
            max_supply=str(faker.pyint(1, 100)),
            cmc_id=faker.pyint(1, 100000000),
        ).to_dict()

        return CryptoAsset(
            **{**base_entity, **kwargs}
        )

    # def to_dict(self):
    #     return {
    #         "ticker": self.ticker,
    #         "name": self.name,
    #         "slug": self.slug,
    #         "cmc_date_added": self.cmc_date_added,
    #         "num_market_pairs": self.num_market_pairs,
    #         "infinite_supply": self.infinite_supply,
    #         "max_supply": self.max_supply,
    #         "cmc_id": self.cmc_id
    #     }
