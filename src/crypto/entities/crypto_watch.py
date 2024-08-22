from datetime import datetime, timedelta
from enum import Enum
from typing import TYPE_CHECKING, cast

import sqlalchemy as sa
from marshmallow import validates
from sqlalchemy import event
from sqlalchemy.engine.default import DefaultExecutionContext
from sqlalchemy.orm import mapped_column, Mapped, relationship, InstanceEvents

from config import config
from postgres import Base

if TYPE_CHECKING:
    from .crypto_asset import CryptoAsset
    from telegram.entities.tg_chat import TgChat


class WatchInterval(Enum):
    EVERY_10_SECONDS = 'EVERY_10_SECONDS'
    EVERY_30_MINUTES = 'EVERY_30_MINUTES'
    EVERY_1_HOUR = 'EVERY_1_HOUR'
    EVERY_3_HOURS = 'EVERY_3_HOURS'
    EVERY_6_HOURS = 'EVERY_6_HOURS'
    EVERY_12_HOURS = 'EVERY_12_HOURS'
    EVERY_DAY = 'EVERY_DAY'

    # EVERY_WEEK = 'EVERY_WEEK'

    @classmethod
    def get_next_datetime(cls, interval: 'WatchInterval') -> datetime:
        """Gets next execution date starting from now according to the interval"""
        hm = {
            WatchInterval.EVERY_10_SECONDS: timedelta(seconds=10),
            WatchInterval.EVERY_30_MINUTES: timedelta(minutes=30),
            WatchInterval.EVERY_1_HOUR: timedelta(hours=1),
            WatchInterval.EVERY_3_HOURS: timedelta(hours=3),
            WatchInterval.EVERY_6_HOURS: timedelta(hours=6),
            WatchInterval.EVERY_12_HOURS: timedelta(hours=12),
            WatchInterval.EVERY_DAY: timedelta(days=1),
        }

        return datetime.now() + hm[interval]

    @classmethod
    def get_text(cls, interval: 'WatchInterval') -> str:
        hm = {
            WatchInterval.EVERY_10_SECONDS: '10 seconds',
            WatchInterval.EVERY_30_MINUTES: '30 minutes',
            WatchInterval.EVERY_1_HOUR: '1 hour',
            WatchInterval.EVERY_3_HOURS: '3 hours',
            WatchInterval.EVERY_6_HOURS: '6 hours',
            WatchInterval.EVERY_12_HOURS: '12 hours',
            WatchInterval.EVERY_DAY: '1 day',
        }

        return hm[interval]


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

    # https://docs.sqlalchemy.org/en/20/core/defaults.html#context-sensitive-default-functions
    @staticmethod
    def default_next_execution_at(context: DefaultExecutionContext) -> datetime:
        params = context.get_current_parameters()

        value: datetime | None = params.get('next_execution_at', None)
        interval = params.get('interval', None)

        if value is not None:
            assert value > datetime.now(), 'next_execution_at must be in the future'

        if value is None and interval:
            value = WatchInterval.get_next_datetime(interval)

        return value

    next_execution_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        default=default_next_execution_at
    )

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
