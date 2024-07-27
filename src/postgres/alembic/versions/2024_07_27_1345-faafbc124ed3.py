"""empty message

Revision ID: faafbc124ed3
Revises: b49792bf231d
Create Date: 2024-07-27 13:45:17.243340

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'faafbc124ed3'
down_revision: Union[str, None] = 'b49792bf231d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('crypto_asset_tags',
    sa.Column('uuid', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('uuid'),
    sa.UniqueConstraint('name')
    )
    op.create_table('crypto_assets',
    sa.Column('uuid', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('ticker', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('slug', sa.String(), nullable=False),
    sa.Column('cmc_date_added', sa.TIMESTAMP(), nullable=False),
    sa.Column('num_market_pairs', sa.Integer(), nullable=False),
    sa.Column('infinite_supply', sa.Boolean(), nullable=False),
    sa.Column('max_supply', sa.Integer(), nullable=True),
    sa.Column('cmc_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('uuid'),
    sa.UniqueConstraint('cmc_id'),
    sa.UniqueConstraint('ticker')
    )
    op.create_table('crypto_assets_to_asset_tags',
    sa.Column('asset_uuid', sa.UUID(), nullable=False),
    sa.Column('tag_uuid', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['asset_uuid'], ['crypto_assets.uuid'], ),
    sa.ForeignKeyConstraint(['tag_uuid'], ['crypto_asset_tags.uuid'], ),
    sa.PrimaryKeyConstraint('asset_uuid', 'tag_uuid'),
    sa.UniqueConstraint('asset_uuid', 'tag_uuid')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('crypto_assets_to_asset_tags')
    op.drop_table('crypto_assets')
    op.drop_table('crypto_asset_tags')
    # ### end Alembic commands ###
