import inspect

from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from exchanges.binance import BinanceAssetsQueryService
from bot.telegram_bot import TelegramBot


@TelegramBot.router()
class BotInlineQueryRouter:
    def __init__(self, assets_service: BinanceAssetsQueryService):
        self.tg_bot = TelegramBot()
        self.assets_service = assets_service

    @TelegramBot.handle_inline_query()
    async def search(self, message: InlineQuery) -> None:
        assets = (await self.assets_service.get_hot_pairs())

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
        ], cache_time=1)
