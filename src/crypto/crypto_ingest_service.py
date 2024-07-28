import asyncio
import itertools
import logging
import random
from datetime import datetime

from apscheduler.triggers.interval import IntervalTrigger

from cron import CronService
from crypto.crypto_assets_repo import CryptoAssetsRepo
from crypto.entities.crypto_asset import CryptoAsset
from crypto.entities.crypto_asset_quote import CryptoAssetQuote
from crypto.entities.crypto_asset_tag import CryptoAssetTag
from exchanges.binance import BinanceUiApi
from exchanges.binance.dtos.binance_all_coins_dto import BinanceCoinQuoteEntry
from postgres import pg_session
from redis_client import RedisService


class CryptoIngestService:
    def __init__(self, crypto_repo: CryptoAssetsRepo, binance_ui_api: BinanceUiApi, cron: CronService,
                 redis: RedisService):
        self.__crypto_repo = crypto_repo
        self.__binance_ui_api = binance_ui_api
        self.__cron = cron
        self.__redis = redis
        self.__logger = logging.getLogger(self.__class__.__name__)

    @pg_session
    async def lock_ingest_crypto_assets(self) -> None:
        # timeout - 60 seconds
        lock = self.__redis.lock('crypto_ingest', timeout=120)

        # Skip if lock is already acquired
        acquired = await lock.acquire(blocking=False)
        if not acquired:
            return

        try:
            await self.ingest_crypto_assets()
        except Exception as e:
            self.__logger.error(f'Failed to ingest crypto assets: {e}')
        finally:
            await lock.release()

    @pg_session
    async def ingest_crypto_assets(self) -> None:
        self.__logger.info('ingest_crypto_assets: started')

        res = await self.__binance_ui_api.get_all_coins(limit=5000)
        count = 0

        while res.status.total_count and count < res.status.total_count:
            self.__logger.info(
                f'ingest_crypto_assets: processing {len(res.data) + count}/{res.status.total_count} coins')

            assets = list[CryptoAsset]()
            # crypto id from cmc_id <-> new quote
            quotes_hm = dict[int, CryptoAssetQuote]()

            for coin in res.data:
                quote: BinanceCoinQuoteEntry | None = getattr(getattr(coin, 'quote', None), 'USD', None)

                if quote:
                    quotes_hm[coin.id] = CryptoAssetQuote(
                        fully_diluted_market_cap=quote.fully_diluted_market_cap,
                        cmc_last_updated=datetime.now(),
                        market_cap_dominance=quote.market_cap_dominance,
                        percent_change_30d=quote.percent_change_30d,
                        percent_change_1h=quote.percent_change_1h,
                        percent_change_24h=quote.percent_change_24h,
                        percent_change_7d=quote.percent_change_7d,
                        percent_change_60d=quote.percent_change_60d,
                        percent_change_90d=quote.percent_change_90d,
                        market_cap=quote.market_cap,
                        volume_change_24h=quote.volume_change_24h,
                        volume_24h=quote.volume_24h,
                        price=quote.price
                    )

                asset = CryptoAsset(
                    ticker=coin.symbol,
                    name=coin.name,
                    slug=coin.slug,
                    cmc_date_added=datetime.now(),
                    num_market_pairs=coin.num_market_pairs,
                    infinite_supply=coin.infinite_supply,
                    max_supply=str(coin.max_supply) if coin.max_supply else None,
                    cmc_id=coin.id,
                    tags=[CryptoAssetTag(name=tag) for tag in coin.tags]
                )
                assets.append(asset)

            asset_chunks = itertools.batched(assets, 150)

            upsert_count = 0
            # assets_hm = dict[str, CryptoAsset]()

            #
            # Upsert assets
            #
            for chunk in asset_chunks:
                upsert_count += len(chunk)
                self.__logger.info(f'ingest_crypto_assets: upserting {upsert_count}/{len(assets)} assets')
                assets = await self.__crypto_repo.bulk_upsert(chunk, conflict=CryptoAsset.cmc_id)

                for asset in assets:
                    quote = quotes_hm.get(asset.cmc_id)
                    if not quote:
                        continue

                    quote.asset_uuid = asset.uuid

            quote_chunks = itertools.batched(quotes_hm.values(), 150)
            insert_count = 0

            # 
            # Insert quotes
            #
            for chunk in quote_chunks:
                insert_count += len(chunk)
                self.__logger.info(f'ingest_crypto_assets: inserting {insert_count}/{len(quotes_hm)} quotes')
                await self.__crypto_repo.bulk_insert_quotes(chunk)

            count += len(res.data)

            # Sleep for some time to avoid rate limiting
            random_sleep_sec = random.randint(3, 6)
            await asyncio.sleep(random_sleep_sec)

            #
            # Request next batch of coins with updates
            #
            res = await self.__binance_ui_api.get_all_coins(offset=count + 1, limit=5000)

    async def on_module_init(self) -> None:
        self.__cron.add_job(self.ingest_crypto_assets, IntervalTrigger(minutes=10))
