import inspect

from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton

from bot.callbacks import DummyCb
from bot.inline.views.callbacks import AddToFavouritesCb, RemoveFromFavouritesCb
from crypto.entities.crypto_asset import CryptoAsset
from utils import round_if


async def inline_query_result(
        asset: CryptoAsset,
        tg_user_id: int
) -> InlineQueryResultArticle:
    latest_quote = asset.latest_quote

    price = round_if(latest_quote.price)

    change_1h = float(round(latest_quote.percent_change_1h, 2))
    change_24h = float(round(latest_quote.percent_change_24h, 2))
    change_7d = float(round(latest_quote.percent_change_7d, 2))

    change_1h_str = f'<b>+{change_1h}%</b>' if change_1h > 0 else change_1h
    change_24h_str = f'<b>+{change_24h}%</b>' if change_24h > 0 else change_24h
    change_7d_str = f'<b>+{change_7d}%</b>' if change_7d > 0 else change_7d

    indicator_1h = '📉' if change_1h < 0 else '📈'
    indicator_24h = '📉' if change_24h < 0 else '📈'
    indicator_7d = '📉' if change_7d < 0 else '📈'

    return InlineQueryResultArticle(
        id=str(asset.uuid),
        title=f'{asset.name} - {asset.ticker}',
        thumbnail_url=asset.large_logo_url,
        hide_url=True,
        description=inspect.cleandoc(f"""
            💸 Price: ${price}
            {indicator_1h} {change_1h} in 1h
            {indicator_24h} {change_24h} in 24h
        """),
        input_message_content=InputTextMessageContent(
            message_text=inspect.cleandoc(f"""
                <b>{asset.ticker}</b> - <a href="https://coinmarketcap.com/currencies/{asset.slug}">{asset.name}</a>

                💸 <b>Price:</b> ${price}
                <blockquote expandable>{indicator_1h} {change_1h_str} in 1h
                {indicator_24h} {change_24h_str} in 24h
                {indicator_7d} {change_7d_str} in 7d
                </blockquote>\n
            """),
            disable_web_page_preview=True,
            parse_mode=ParseMode.HTML,
        ),
        reply_markup=await render_query_result_reply_markup(
            favourite=False,
            tg_user_id=tg_user_id,
            asset_uuid=str(asset.uuid)
        )
    )


async def render_query_result_reply_markup(
        tg_user_id: int,
        asset_uuid: str,
        favourite: bool = False,
) -> InlineKeyboardMarkup:
    if favourite:
        cb_data = await RemoveFromFavouritesCb(
            tg_user_id=tg_user_id,
            asset_uuid=asset_uuid
        ).save()

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='Favourite 💫',
                        callback_data=cb_data
                    )
                ]
            ]
        )

    cb_data = await AddToFavouritesCb(
        tg_user_id=tg_user_id,
        asset_uuid=asset_uuid
    ).save()

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Save ⭐️',
                    callback_data=cb_data
                )
            ]
        ]
    )
