from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from postgres import Base
import sqlalchemy as sa

from utils import faker
from .crypto_asset_to_asset_tag import CryptoAssetToAssetTag

if TYPE_CHECKING:
    from .crypto_asset import CryptoAsset


class CryptoAssetTag(Base):
    __tablename__ = 'crypto_asset_tags'

    uuid: Mapped[sa.UUID] = mapped_column(sa.UUID, primary_key=True, server_default=sa.func.gen_random_uuid())
    name: Mapped[str] = mapped_column(sa.String, unique=True, nullable=False)

    assets: Mapped[list['CryptoAsset']] = relationship(
        secondary=CryptoAssetToAssetTag.__table__,
        back_populates='tags',
        lazy='noload'
    )

    @staticmethod
    def random() -> 'CryptoAssetTag':
        return CryptoAssetTag(
            name=faker.pystr(10)
        )
