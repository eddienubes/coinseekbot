import inspect

from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton

from bot.callbacks import DummyCallback
from bot.watch.callbacks import WatchCallback
from crypto.entities.crypto_asset import CryptoAsset
from utils import round_if


def inline_query_result(asset: CryptoAsset) -> InlineQueryResultArticle:
    price = round_if(asset.latest_quote.price)
    change_24h = round(asset.latest_quote.percent_change_24h, 2)
    indicator = '📉' if change_24h < 0 else '📈'

    return InlineQueryResultArticle(
        id=str(asset.uuid),
        title=f'{asset.name} - {asset.ticker}',
        thumbnail_url=asset.large_logo_url,
        hide_url=True,
        description=inspect.cleandoc(f"""
            💸 Price: ${price}
            {indicator} {change_24h}% in 24h
        """),
        input_message_content=InputTextMessageContent(
            message_text=inspect.cleandoc(f"""
                <b>{asset.ticker}</b> - <code>{asset.name}</code>

                💸 <b>Price:</b> ${price}
                <blockquote>{indicator} {change_24h}% in 24h</blockquote>
            """),
            disable_web_page_preview=True,
            parse_mode=ParseMode.HTML,
        ),
        reply_markup=_reply_markup(watching=False)
    )


def _reply_markup(watching: bool = False) -> InlineKeyboardMarkup:
    if watching:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='Watching ✅',
                        callback_data=DummyCallback().pack()
                    )
                ]
            ]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Watch 👀',
                    callback_data=WatchCallback().pack()
                )
            ]
        ]
    )
