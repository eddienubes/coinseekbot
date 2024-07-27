from sqlalchemy.orm import Mapped, mapped_column

from postgres import Base
import sqlalchemy as sa


class CryptoAssetToAssetTag(Base):
    __tablename__ = 'crypto_assets_to_asset_tags'

    asset_uuid: Mapped[sa.UUID] = mapped_column(sa.UUID, sa.ForeignKey('crypto_assets.uuid'), primary_key=True)
    tag_uuid: Mapped[sa.UUID] = mapped_column(sa.UUID, sa.ForeignKey('crypto_asset_tags.uuid'), primary_key=True)

    __table_args__ = (
        sa.UniqueConstraint('asset_uuid', 'tag_uuid'),
    )
