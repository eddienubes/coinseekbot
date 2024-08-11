from aiogram.types import InlineQuery

from config import config
from crypto.crypto_assets_repo import CryptoAssetsRepo
from crypto.entities.crypto_asset import CryptoAsset
from exchanges.binance import BinanceAssetsQueryService
from ..watch.views import inline_query_result
from ..telegram_bot import TelegramBot


@TelegramBot.router()
class BotInlineQueryRouter:
    def __init__(self,
                 assets_service: BinanceAssetsQueryService,
                 crypto_repo: CryptoAssetsRepo,
                 ):
        self.crypto_repo = crypto_repo
        self.assets_service = assets_service

    @TelegramBot.handle_inline_query()
    async def search(self, message: InlineQuery) -> None:
        async def _(els: list[CryptoAsset], hot: bool = False):
            answers = list()

            for asset in els:
                answers.append(inline_query_result(
                    asset,
                    tg_user_id=message.from_user.id
                ))

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
                ticker = asset.assetCode.upper()
                if ticker in found_assets_hm:
                    restored_order.append(found_assets_hm[ticker])

            await _(restored_order)
            return

        search_hits = await self.crypto_repo.get_with_latest_quote(tickers=[message.query], fuzzy=True, dedupe=False)

        await _(search_hits)
