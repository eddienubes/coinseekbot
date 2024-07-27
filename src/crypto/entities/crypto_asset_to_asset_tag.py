from postgres import Base
import sqlalchemy as sa

crypto_to_asset_tag = sa.Table(
    'crypto_assets_to_asset_tags',
    Base.metadata,
    sa.Column('asset_uuid', sa.ForeignKey('crypto_assets.uuid'), primary_key=True),
    sa.Column('tag_uuid', sa.ForeignKey('crypto_asset_tags.uuid'), primary_key=True),
    sa.UniqueConstraint('asset_uuid', 'tag_uuid'),
)
