import asyncio
import inspect

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from crypto.entities.crypto_asset import CryptoAsset
from crypto.entities.crypto_favourite import CryptoFavourite
from crypto.entities.crypto_watch import WatchInterval
from utils import Pageable
from .callbacks import WatchSelectIntervalCb, StartWatchingCb, StopWatchingCb, StopWatchingConfirmationCb, \
    WatchListFavouritesCb

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
        favourites: Pageable[CryptoFavourite]
) -> InlineKeyboardMarkup:
    btns = []

    for fav in favourites.hits:
        if fav.watch:
            postfix = f'- Watching 👀'
            cb_data = StopWatchingConfirmationCb(
                tg_user_id=tg_user_id,
                asset_uuid=str(fav.asset_uuid)
            ).pack()
        else:
            cb_data = WatchSelectIntervalCb(
                asset_uuid=str(fav.asset_uuid),
                tg_user_id=tg_user_id
            ).pack()
            postfix = ''

        row = [
            InlineKeyboardButton(
                text=f'{fav.asset.name} {postfix}',
                callback_data=cb_data
            )
        ]

        btns.append(row)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            *btns
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
                    callback_data=WatchListFavouritesCb(
                        tg_user_id=tg_user_id
                    ).pack()
                )
            ]
        ]
    )
