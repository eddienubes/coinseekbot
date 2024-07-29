import inspect

from aiogram.enums import ParseMode
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from bot.telegram_bot import TelegramBot
from config import config
from crypto.crypto_assets_repo import CryptoAssetsRepo
from crypto.entities.crypto_asset import CryptoAsset
from exchanges.binance import BinanceAssetsQueryService
from utils.math_utils import round_if


@TelegramBot.router()
class BotInlineQueryRouter:
    def __init__(self,
                 assets_service: BinanceAssetsQueryService,
                 crypto_repo: CryptoAssetsRepo,
                 ):
        self.tg_bot = TelegramBot()
        self.crypto_repo = crypto_repo
        self.assets_service = assets_service

    @TelegramBot.handle_inline_query()
    async def search(self, message: InlineQuery) -> None:
        async def _(els: list[CryptoAsset], hot: bool = False):
            answers = list()

            for asset in els:
                price = round_if(asset.latest_quote.price)
                change_24h = round(asset.latest_quote.percent_change_24h, 2)
                indicator = '📉' if change_24h < 0 else '📈'

                answers.append(
                    InlineQueryResultArticle(
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
                            parse_mode=ParseMode.HTML
                        )
                    )
                )

            cache_time = config.bot_inline_hot_cache_timeout_sec \
                if hot else config.bot_inline_cache_timeout_sec

            await message.answer(answers, cache_time=cache_time)

        # fewer than 2 characters, return hot assets
        if len(message.query) < 2:
            hot_assets = (await self.assets_service.get_hot_pairs())

            tickers = [asset.assetCode.upper() for asset in hot_assets]

            found_assets = await self.crypto_repo.get_with_latest_quote(tickers, dedupe=True)
            found_assets_hm = dict[str, CryptoAsset]()
            for asset in found_assets:
                found_assets_hm[asset.ticker] = asset

            restored_order = list()

            for asset in hot_assets:
                restored_order.append(found_assets_hm[asset.assetCode.upper()])

            await _(restored_order)
            return

        search_hits = await self.crypto_repo.get_with_latest_quote(tickers=[message.query], fuzzy=True, dedupe=False)

        await _(search_hits)
