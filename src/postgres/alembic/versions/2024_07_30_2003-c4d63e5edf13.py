"""empty message

Revision ID: c4d63e5edf13
Revises: 81f063142aed
Create Date: 2024-07-30 20:03:46.398880

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4d63e5edf13'
down_revision: Union[str, None] = '81f063142aed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('crypto_chat_watches',
    sa.Column('uuid', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('asset_uuid', sa.UUID(), nullable=False),
    sa.Column('tg_chat_uuid', sa.UUID(), nullable=False),
    sa.Column('interval', sa.Enum('EVERY_30_MINUTES', 'EVERY_1_HOUR', 'EVERY_3_HOURS', 'EVERY_6_HOURS', 'EVERY_12_HOURS', 'EVERY_DAY', 'EVERY_WEEK', name='watchinterval', native_enum=False, length=None), nullable=False),
    sa.Column('next_execution_at', sa.TIMESTAMP(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['asset_uuid'], ['crypto_assets.uuid'], ),
    sa.ForeignKeyConstraint(['tg_chat_uuid'], ['tg_chats.uuid'], ),
    sa.PrimaryKeyConstraint('uuid'),
    sa.UniqueConstraint('asset_uuid', 'tg_chat_uuid')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('crypto_chat_watches')
    # ### end Alembic commands ###
