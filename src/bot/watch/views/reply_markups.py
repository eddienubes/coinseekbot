import asyncio
import inspect

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from crypto.entities.crypto_asset import CryptoAsset
from crypto.entities.crypto_watch import WatchInterval
from .callbacks import WatchSelectIntervalCb

WATCH_INTERVALS_TEXT = {
    WatchInterval.EVERY_30_MINUTES: '30 minutes',
    WatchInterval.EVERY_1_HOUR: '1 hours',
    WatchInterval.EVERY_3_HOURS: '3 hours',
    WatchInterval.EVERY_6_HOURS: '6 hours',
    WatchInterval.EVERY_12_HOURS: '12 hours',
    WatchInterval.EVERY_DAY: '1 day',
    # WatchInterval.EVERY_WEEK: '1 week',
}


async def render_watch_select_text(
        asset: CryptoAsset,
) -> str:
    text = inspect.cleandoc(f"""
                <b>{asset.ticker}</b> - <code>{asset.name}</code>
                <b>Watch 👀</b>

                <blockquote>Select notification interval 👇</blockquote>
            """)

    return text


async def render_watch_select_interval(
        tg_user_id: int,
        asset_uuid: str
) -> InlineKeyboardMarkup:
    async def _(interval: WatchInterval):
        cb_data = await WatchSelectIntervalCb(
            tg_user_id=tg_user_id,
            asset_uuid=asset_uuid,
            interval=interval
        ).save()

        return cb_data, interval

    cbs = list(await asyncio.gather(
        *[
            _(interval)
            for interval in list(WatchInterval)
        ]
    ))

    btns = [[InlineKeyboardButton(
        text=WATCH_INTERVALS_TEXT[interval],
        callback_data=cb
    )] for cb, interval in cbs]

    return InlineKeyboardMarkup(
        inline_keyboard=[
            *btns
        ]
    )
