from typing import cast, TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from postgres import Base
import sqlalchemy as sa

if TYPE_CHECKING:
    from .crypto_asset import CryptoAsset
    from .crypto_watch import CryptoWatch


class CryptoFavourite(Base):
    __tablename__ = 'crypto_favourites'

    uuid: Mapped[sa.UUID] = mapped_column(sa.UUID, primary_key=True, server_default=sa.func.gen_random_uuid())

    asset_uuid: Mapped[sa.UUID] = mapped_column(sa.ForeignKey('crypto_assets.uuid'), nullable=False)
    tg_user_uuid: Mapped[sa.UUID] = mapped_column(sa.ForeignKey('tg_users.uuid'), nullable=False)

    asset: Mapped['CryptoAsset'] = relationship(
        'CryptoAsset',
        lazy='joined',
        # I don't fucking know why, but typing has broken here
        foreign_keys=cast(list[sa.Column], [asset_uuid])
    )

    watch: Mapped['CryptoWatch'] = relationship(
        lazy='joined',
        primaryjoin='CryptoFavourite.asset_uuid == foreign(CryptoWatch.asset_uuid)',
        uselist=False
    )

    __table_args__ = (
        sa.UniqueConstraint('asset_uuid', 'tg_user_uuid'),
    )
