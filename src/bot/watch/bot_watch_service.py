import asyncio
import logging

from datetime import datetime, timedelta

from apscheduler.triggers.interval import IntervalTrigger

from bot import TelegramBot
from bot.watch.views.views import render_watch_notification_text
from cron import CronService
from crypto.crypto_watches_repo import CryptoWatchesRepo
from crypto.entities.crypto_watch import WatchInterval, CryptoWatch
from redis_client import RedisService
from telegram.tg_chats_repo import TgChatsRepo
from telegram.tg_users_repo import TgUsersRepo

CRYPTO_INTERVAL_TO_TIMEDELTA = {
    WatchInterval.EVERY_10_SECONDS: timedelta(seconds=1),
    WatchInterval.EVERY_30_MINUTES: timedelta(minutes=30),
    WatchInterval.EVERY_1_HOUR: timedelta(hours=1),
    WatchInterval.EVERY_3_HOURS: timedelta(hours=3),
    WatchInterval.EVERY_6_HOURS: timedelta(hours=6),
    WatchInterval.EVERY_12_HOURS: timedelta(hours=12),
    WatchInterval.EVERY_DAY: timedelta(days=1),
}


class BotWatchService:
    def __init__(
            self,
            tg_users_repo: TgUsersRepo,
            tg_chats_repo: TgChatsRepo,
            watches_repo: CryptoWatchesRepo,
            cron: CronService,
            redis: RedisService,
            tg_bot: TelegramBot
    ):
        self.__tg_users_repo = tg_users_repo
        self.__tg_chats_repo = tg_chats_repo
        self.__watches_repo = watches_repo
        self.__cron = cron
        self.__redis = redis
        self.__tg_bot = tg_bot
        self.__logger = logging.getLogger(self.__class__.__name__)

    async def notify(self) -> None:
        self.__logger.info('notify: started')

        watches = await self.__watches_repo.get_watches_to_notify()

        async with asyncio.TaskGroup() as tg:
            for watch in watches:
                self.__logger.info(
                    f'notify: processing watch interval {watch.interval}, tg_chat_id: {watch.tg_chat.tg_id}, asset_name: {watch.asset.name}')

                if watch.next_execution_at is None:
                    watch.next_execution_at = datetime.now() + CRYPTO_INTERVAL_TO_TIMEDELTA[watch.interval]
                    continue

                async def _(w: CryptoWatch):
                    try:
                        self.__logger.info(
                            f'notify: sending notification for watch interval {w.interval}, asset_name: {w.asset.name}')
                        await self.__tg_bot.bot.send_message(
                            chat_id=watch.tg_chat.tg_id,
                            text=render_watch_notification_text(watch, watch.asset, watch.asset.latest_quote)
                        )
                        w.next_execution_at = datetime.now() + CRYPTO_INTERVAL_TO_TIMEDELTA[w.interval]
                        self.__logger.info(
                            f'notify: sent notification for watch interval {w.interval}, asset_name: {w.asset.name}'
                        )
                    except Exception as e:
                        self.__logger.error(
                            f'Failed to send notification for a watch interval: {w.interval}, asset name: {w.asset.name} error: {e}'
                        )

                tg.create_task(_(watch))
        await self.__watches_repo.bulk_upsert(watches)

    async def lock_notify(self) -> None:
        # timeout - 150 seconds
        lock = self.__redis.lock('bot_watch_notify', timeout=150)

        # Skip if lock is already acquired
        acquired = await lock.acquire(blocking=False)
        if not acquired:
            return

        try:
            await self.notify()
        except Exception as e:
            self.__logger.error(f'Failed to notify watches: {e}')
        finally:
            await lock.release()

    async def on_module_init(self):
        now = datetime.now()

        self.__cron.add_job(self.lock_notify, IntervalTrigger(seconds=5))
