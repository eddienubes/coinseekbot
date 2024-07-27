from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import mapped_column, Mapped, relationship
import sqlalchemy as sa

from postgres import Base
from utils import faker
from .crypto_asset_to_asset_tag import crypto_to_asset_tag

if TYPE_CHECKING:
    from .crypto_asset_tag import CryptoAssetTag


class CryptoAsset(Base):
    __tablename__ = 'crypto_assets'

    uuid: Mapped[sa.UUID] = mapped_column(sa.UUID, primary_key=True, server_default=sa.func.gen_random_uuid())
    ticker: Mapped[str] = mapped_column(sa.String, unique=True, nullable=False)

    name: Mapped[str] = mapped_column(sa.String, unique=False, nullable=False)
    slug: Mapped[str] = mapped_column(sa.String, unique=False, nullable=False)

    cmc_date_added: Mapped[datetime] = mapped_column(sa.TIMESTAMP, nullable=False)
    num_market_pairs: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    infinite_supply: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=False)
    max_supply: Mapped[int] = mapped_column(sa.Integer, nullable=True)

    cmc_id: Mapped[int] = mapped_column(sa.Integer, unique=True, nullable=False)

    tags: Mapped[list['CryptoAssetTag']] = relationship(
        secondary=crypto_to_asset_tag,
        back_populates='assets'
    )

    @staticmethod
    def random():
        return CryptoAsset(
            ticker=faker.pystr(10, 10),
            name=faker.pystr(10, 10),
            slug=faker.pystr(10, 10),
            cmc_date_added=datetime.now(),
            num_market_pairs=faker.pyint(1, 100),
            infinite_supply=False,
            max_supply=faker.pyint(1, 100),
            cmc_id=faker.pyint(1, 100000000),
        )
