import inspect

from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from bot.telegram_bot import TelegramBot
from config import config
from exchanges.binance import BinanceAssetsQueryService


@TelegramBot.router()
class BotInlineQueryRouter:
    def __init__(self, assets_service: BinanceAssetsQueryService):
        self.tg_bot = TelegramBot()
        self.assets_service = assets_service

    @TelegramBot.handle_inline_query()
    async def search(self, message: InlineQuery) -> None:
        async def _(assets):
            await message.answer([
                InlineQueryResultArticle(
                    id=asset.symbol,
                    title=f'{asset.symbol}',
                    thumbnail_url=asset.logoUrl,
                    hide_url=True,
                    description=inspect.cleandoc(f"""
                        💰 Price: 1.234 USDT
                        🔸 +100% in 24h
                    """),
                    input_message_content=InputTextMessageContent(
                        message_text=asset.symbol,
                        disable_web_page_preview=True
                    )
                ) for asset in assets
            ], cache_time=config.bot_inline_cache_timeout_sec)

        # fewer than 2 characters, return hot assets
        if not len(message.query) < 2:
            assets = (await self.assets_service.get_hot_pairs())

            await _(assets)
            return

        # search for assets
       