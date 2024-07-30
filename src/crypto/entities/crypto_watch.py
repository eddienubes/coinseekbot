from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, cast, Sequence

import sqlalchemy as sa
from sqlalchemy.orm import mapped_column, Mapped, relationship

from postgres import Base

if TYPE_CHECKING:
    from .crypto_asset import CryptoAsset
    from telegram.tg_chat import TgChat


class WatchInterval(Enum):
    EVERY_30_MINUTES = 'EVERY_30_MINUTES'
    EVERY_1_HOUR = 'EVERY_1_HOUR'
    EVERY_3_HOURS = 'EVERY_3_HOURS'
    EVERY_6_HOURS = 'EVERY_6_HOURS'
    EVERY_12_HOURS = 'EVERY_12_HOURS'
    EVERY_DAY = 'EVERY_DAY'
    EVERY_WEEK = 'EVERY_WEEK'


class CryptoWatch(Base):
    __tablename__ = 'crypto_chat_watches'

    uuid: Mapped[sa.UUID] = mapped_column(sa.UUID, primary_key=True, server_default=sa.func.gen_random_uuid())

    asset_uuid: Mapped[sa.UUID] = mapped_column(sa.ForeignKey('crypto_assets.uuid'), nullable=False)
    tg_chat_uuid: Mapped[sa.UUID] = mapped_column(sa.ForeignKey('tg_chats.uuid'), nullable=False)
    interval: Mapped[WatchInterval] = mapped_column(sa.Enum(WatchInterval, native_enum=False, length=None),
                                                    nullable=False)

    next_execution_at: Mapped[datetime] = mapped_column(sa.TIMESTAMP, nullable=True)

    asset: Mapped['CryptoAsset'] = relationship(
        'CryptoAsset',
        lazy='joined',
        # I don't fucking know why, but typing has broken here
        foreign_keys=cast(list[sa.Column], [asset_uuid])
    )

    tg_chat: Mapped['TgChat'] = relationship(
        'TgChat',
        lazy='joined',
        # I don't fucking know why, but typing has broken here
        foreign_keys=cast(list[sa.Column], [tg_chat_uuid])
    )

    __table_args__ = (
        sa.UniqueConstraint('asset_uuid', 'tg_chat_uuid'),
    )
