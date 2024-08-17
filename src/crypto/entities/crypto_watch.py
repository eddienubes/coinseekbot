from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, cast

import sqlalchemy as sa
from marshmallow import validates
from sqlalchemy.orm import mapped_column, Mapped, relationship

from postgres import Base

if TYPE_CHECKING:
    from .crypto_asset import CryptoAsset
    from telegram.entities.tg_chat import TgChat


class WatchInterval(Enum):
    EVERY_30_MINUTES = 'EVERY_30_MINUTES'
    EVERY_1_HOUR = 'EVERY_1_HOUR'
    EVERY_3_HOURS = 'EVERY_3_HOURS'
    EVERY_6_HOURS = 'EVERY_6_HOURS'
    EVERY_12_HOURS = 'EVERY_12_HOURS'
    EVERY_DAY = 'EVERY_DAY'
    # EVERY_WEEK = 'EVERY_WEEK'


class CryptoWatchStatus(Enum):
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'


class CryptoWatch(Base):
    __tablename__ = 'crypto_chat_watches'

    uuid: Mapped[sa.UUID] = mapped_column(sa.UUID, primary_key=True, server_default=sa.func.gen_random_uuid())

    asset_uuid: Mapped[sa.UUID] = mapped_column(sa.ForeignKey('crypto_assets.uuid'), nullable=False)
    tg_chat_uuid: Mapped[sa.UUID] = mapped_column(sa.ForeignKey('tg_chats.uuid'), nullable=False)
    interval: Mapped[WatchInterval] = mapped_column(
        sa.Enum(WatchInterval, native_enum=False, length=None),
        nullable=False
    )

    status: Mapped[CryptoWatchStatus] = mapped_column(
        sa.Enum(CryptoWatchStatus, native_enum=False, length=None),
        nullable=False,
        default=CryptoWatchStatus.ACTIVE,
        index=True
    )

    next_execution_at: Mapped[datetime | None] = mapped_column(
        sa.TIMESTAMP,
        nullable=True
    )

    @validates('next_execution_at')
    def validate_next_execution_at(self, value: datetime | None) -> datetime | None:
        if value is not None:
            assert value > datetime.now(), 'next_execution_at must be in the future'
        return value

    asset: Mapped['CryptoAsset'] = relationship(
        'CryptoAsset',
        lazy='noload',
        # I don't fucking know why, but typing has broken here
        foreign_keys=cast(list[sa.Column], [asset_uuid]),
        viewonly=True
    )

    tg_chat: Mapped['TgChat'] = relationship(
        'TgChat',
        lazy='noload',
        # I don't fucking know why, but typing has broken here
        foreign_keys=cast(list[sa.Column], [tg_chat_uuid])
    )

    __table_args__ = (
        sa.UniqueConstraint('asset_uuid', 'tg_chat_uuid'),
    )
