import asyncio
import itertools
import logging
import random
from datetime import datetime, timedelta

from dateutil import parser as date_parser
from apscheduler.triggers.interval import IntervalTrigger

from config import config
from cron import CronService
from crypto.crypto_assets_repo import CryptoAssetsRepo
from crypto.entities.crypto_asset import CryptoAsset
from crypto.entities.crypto_asset_quote import CryptoAssetQuote
from crypto.entities.crypto_asset_tag import CryptoAssetTag
from exchanges.binance import BinanceUiApi
from exchanges.binance.dtos.binance_all_coins_dto import BinanceCoinQuoteEntry
from postgres import pg_session
from redis_client import RedisService
from utils import dispatch


class CryptoIngestService:
    def __init__(self,
                 crypto_repo: CryptoAssetsRepo,
                 binance_ui_api: BinanceUiApi,
                 cron: CronService,
                 redis: RedisService
                 ):
        self.__crypto_repo = crypto_repo
        self.__binance_ui_api = binance_ui_api
        self.__cron = cron
        self.__redis = redis
        self.__logger = logging.getLogger(self.__class__.__name__)

    @pg_session
    async def lock_ingest_crypto_asset_quotes(self) -> None:
        # timeout - 150 seconds
        lock = self.__redis.lock('crypto_ingest', timeout=150)

        # Skip if lock is already acquired
        acquired = await lock.acquire(blocking=False)
        if not acquired:
            return

        try:
            await self.ingest_crypto_asset_quotes()
        except Exception as e:
            self.__logger.error(f'Failed to ingest crypto asset quotes: {e}')
        finally:
            await lock.release()

    @pg_session
    async def lock_ingest_crypto_assets(self) -> None:
        # timeout - 150 seconds
        lock = self.__redis.lock('crypto_ingest', timeout=150)

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
    async def ingest_crypto_asset_quotes(self) -> None:
        self.__logger.info('ingest_crypto_asset_quotes: started')

        res = await self.__binance_ui_api.get_all_coins(limit=5000)
        count = 0

        while res.status.total_count and count < res.status.total_count:
            self.__logger.info(
                f'ingest_crypto_asset_quotes: processing {len(res.data) + count}/{res.status.total_count} coins')

            # crypto id from cmc_id <-> new quote
            quotes_hm = dict[int, CryptoAssetQuote]()

            assets = await self.__crypto_repo.get_by_cmc_ids([coin.id for coin in res.data])
            assets_hm = {asset.cmc_id: asset for asset in assets}

            for coin in res.data:
                quote: BinanceCoinQuoteEntry | None = getattr(getattr(coin, 'quote', None), 'USD', None)

                if not quote or coin.id not in assets_hm:
                    continue

                asset = assets_hm[coin.id]

                quote_entity = CryptoAssetQuote(
                    cmc_last_updated=date_parser.parse(quote.last_updated),
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
                    price=quote.price,
                    asset_uuid=asset.uuid
                )

                # has_quote_changed = await self.has_quote_changed(quote_entity)
                # 
                # if has_quote_changed:

                quotes_hm[coin.id] = quote_entity

            quote_chunks = itertools.batched(quotes_hm.values(), 150)
            insert_count = 0

            #
            # Insert quote
            #
            for chunk in quote_chunks:
                upserted_quotes = await self.__crypto_repo.bulk_upsert_quotes(chunk)

                insert_count += len(upserted_quotes)
                self.__logger.info(f'ingest_crypto_asset_quotes: inserted {insert_count}/{len(quotes_hm)} quotes')

            count += len(res.data)

            # Sleep for some time to avoid rate limiting
            random_sleep_sec = random.randint(3, 6)
            await asyncio.sleep(random_sleep_sec)

            #
            # Request next batch of coins with updates
            #
            res = await self.__binance_ui_api.get_all_coins(offset=count + 1, limit=5000)

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

            for coin in res.data:
                asset = CryptoAsset(
                    ticker=coin.symbol,
                    name=coin.name,
                    slug=coin.slug,
                    cmc_date_added=date_parser.parse(coin.date_added).replace(tzinfo=None),
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
                upserted_assets = await self.__crypto_repo.bulk_upsert(chunk, conflict=CryptoAsset.cmc_id)

                upsert_count += len(upserted_assets)

                self.__logger.info(f'ingest_crypto_assets: upserted {upsert_count}/{len(assets)} assets')

            count += len(res.data)

            # Sleep for some time to avoid rate limiting
            random_sleep_sec = random.randint(3, 6)
            await asyncio.sleep(random_sleep_sec)

            #
            # Request next batch of coins with updates
            #
            res = await self.__binance_ui_api.get_all_coins(offset=count + 1, limit=5000)

    async def has_quote_changed(self, quote: CryptoAssetQuote) -> bool:
        quote_hash = str(hash(quote))

        key = f'quote:{quote.asset_uuid}'

        existing_hash = await self.__redis.get(key)

        if existing_hash == quote_hash:
            return False

        await self.__redis.set(key, quote_hash)

        return True

    async def on_module_init(self) -> None:
        # Start the job in the next hour
        if config.env == 'test' or not config.seed_crypto_enabled:
            return

        async def _():
            await self.lock_ingest_crypto_assets()
            await self.lock_ingest_crypto_asset_quotes()

        dispatch(_())

        start_time = datetime.now() + timedelta(hours=24)
        self.__cron.add_job(self.lock_ingest_crypto_assets, IntervalTrigger(hours=24, start_time=start_time))

        start_time = datetime.now() + timedelta(minutes=15)
        self.__cron.add_job(self.lock_ingest_crypto_asset_quotes, IntervalTrigger(minutes=15, start_time=start_time))
