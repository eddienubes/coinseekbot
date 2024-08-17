import asyncio
import inspect

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import config
from crypto.entities.crypto_asset import CryptoAsset
from crypto.entities.crypto_asset_quote import CryptoAssetQuote
from crypto.entities.crypto_favourite import CryptoFavourite
from crypto.entities.crypto_watch import WatchInterval, CryptoWatch, CryptoWatchStatus
from utils import Pageable
from .callbacks import WatchSelectIntervalCb, StartWatchingCb, StopWatchingCb, StopWatchingConfirmationCb, \
    WatchlistFavouritesCb, WatchlistPageCb
from ...callbacks import DummyCb

WATCH_INTERVALS_TEXT = {
    WatchInterval.EVERY_30_MINUTES: '30 minutes',
    WatchInterval.EVERY_1_HOUR: '1 hours',
    WatchInterval.EVERY_3_HOURS: '3 hours',
    WatchInterval.EVERY_6_HOURS: '6 hours',
    WatchInterval.EVERY_12_HOURS: '12 hours',
    WatchInterval.EVERY_DAY: '1 day',
    # WatchInterval.EVERY_WEEK: '1 week',
}


def render_watch_select_text(
        asset: CryptoAsset,
) -> str:
    text = inspect.cleandoc(f"""
                <b>{asset.ticker}</b> - <code>{asset.name}</code>
                <b>Watch 👀</b>

                <blockquote>Select notification interval 👇</blockquote>
            """)

    return text


async def render_start_watching_list(
        tg_user_id: int,
        asset_uuid: str
) -> InlineKeyboardMarkup:
    async def _(interval: WatchInterval):
        cb_data = await StartWatchingCb(
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


def render_favourites_list(
        tg_user_id: int,
        watchlist: Pageable[CryptoWatch | CryptoFavourite]
) -> InlineKeyboardMarkup:
    btns = []

    for item in watchlist.hits:
        is_watch = isinstance(item, CryptoWatch)

        if is_watch:
            watch = item
        else:
            watch = item.watch

        # Watch might not be defined, if it's of a favourite asset
        if watch and watch.status == CryptoWatchStatus.ACTIVE:
            postfix = f'💫 - Watching 👀' if not is_watch else ' - Watching 👀'
            cb_data = StopWatchingConfirmationCb(
                tg_user_id=tg_user_id,
                asset_uuid=str(item.asset_uuid)
            ).pack()
        else:
            cb_data = WatchSelectIntervalCb(
                asset_uuid=str(item.asset_uuid),
                tg_user_id=tg_user_id
            ).pack()
            postfix = '💫' if not is_watch else ''

        row = [
            InlineKeyboardButton(
                text=f'{item.asset.name} {postfix}',
                callback_data=cb_data
            )
        ]

        btns.append(row)

    print('has_previous_page', watchlist.has_previous_page())
    print('has_next_page', watchlist.has_next_page())
    print('is_pageable', watchlist.is_pageable())
    print('get_current_page', watchlist.get_current_page())
    print('get_total_pages', watchlist.get_total_pages())
    print('get_next_offset', watchlist.get_next_offset())
    print('get_previous_offset', watchlist.get_previous_offset())

    if not watchlist.is_pageable():
        return InlineKeyboardMarkup(
            inline_keyboard=[
                *btns
            ]
        )

    last_row = [
        InlineKeyboardButton(
            text=f'{watchlist.get_current_page()}/{watchlist.get_total_pages()}',
            callback_data=DummyCb().pack()
        )
    ]

    if watchlist.has_previous_page():
        last_row.insert(0, InlineKeyboardButton(
            text='⬅️',
            callback_data=WatchlistPageCb(
                tg_user_id=tg_user_id,
                offset=watchlist.get_previous_offset()
            ).pack()
        ))

    if watchlist.has_next_page():
        last_row.append(InlineKeyboardButton(
            text='➡️',
            callback_data=WatchlistPageCb(
                tg_user_id=tg_user_id,
                offset=watchlist.get_next_offset()
            ).pack()
        ))

    return InlineKeyboardMarkup(
        inline_keyboard=[
            *btns,
            last_row
        ]
    )


def render_favourite_list_text() -> str:
    return inspect.cleandoc(f"""
        <b>Watch your favourite assets</b>
    """)


def render_stop_watching_confirm_text(asset: CryptoAsset) -> str:
    return inspect.cleandoc(f"""
        <b>{asset.ticker}</b> - <code>{asset.name}</code>

        <b>😧 Are you sure you want to stop watching this asset?</b>
    """)


def render_stop_watching_confirm_reply_markup(
        tg_user_id: int,
        asset_uuid: str
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Yes, I am sure',
                    callback_data=StopWatchingCb(
                        tg_user_id=tg_user_id,
                        asset_uuid=asset_uuid
                    ).pack()
                ),
                InlineKeyboardButton(
                    text='Nope, not yet',
                    callback_data=WatchlistFavouritesCb(
                        tg_user_id=tg_user_id
                    ).pack()
                )
            ]
        ]
    )


def render_watch_notification_text(watches: list[CryptoWatch]) -> str:
    body = ''

    for watch in watches:
        latest_quote = watch.asset.latest_quote
        asset = watch.asset

        change_1h = float(round(latest_quote.percent_change_1h, 2))
        change_24h = float(round(latest_quote.percent_change_24h, 2))
        change_7d = float(round(latest_quote.percent_change_7d, 2))

        change_1h_str = f'<b>+{change_1h}%</b>' if change_1h > 0 else change_1h
        change_24h_str = f'<b>+{change_24h}%</b>' if change_24h > 0 else change_24h
        change_7d_str = f'<b>+{change_7d}%</b>' if change_7d > 0 else change_7d

        indicator_1h = '📉' if change_1h < 0 else '📈'
        indicator_24h = '📉' if change_24h < 0 else '📈'
        indicator_7d = '📉' if change_7d < 0 else '📈'

        body += inspect.cleandoc(f"""
            <blockquote expandable><a href="https://coinmarketcap.com/currencies/{asset.name.replace(' ', '').lower()}">{asset.name}</a>
            {indicator_1h} {change_1h_str} in 1h
            {indicator_24h} {change_24h_str} in 24h
            {indicator_7d} {change_7d_str} in 7d
            </blockquote>\n
        """)

    return inspect.cleandoc(f"""
        👀 Your watchlist:
        {body}
    """)
