from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from crypto.entities.crypto_watch import WatchInterval
from .callbacks import WatchSelectIntervalCb


def watch_select_interval(
        tg_user_id: int,
        asset_uuid: str
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            list(
                map(
                    lambda interval: InlineKeyboardButton(
                        text=interval,
                        callback_data=WatchSelectIntervalCb(
                            tg_user_id=tg_user_id,
                            asset_uuid=asset_uuid,
                            interval=interval
                        ).pack()
                    ),
                    list(WatchInterval)
                )
            )
        ]
    )
