import asyncio
import logging

from datetime import datetime, timedelta

from apscheduler.triggers.interval import IntervalTrigger

from bot import TelegramBot
from bot.watch.views.views import render_watch_notification_text
from config import config
from cron import CronService
from crypto.crypto_watches_repo import CryptoWatchesRepo
from crypto.entities.crypto_watch import WatchInterval, CryptoWatch
from postgres import pg_session
from redis_client import RedisService
from telegram.tg_chats_repo import TgChatsRepo
from telegram.tg_users_repo import TgUsersRepo


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

    @pg_session
    async def notify(self) -> None:
        self.__logger.info('notify: started')

        watches = await self.__watches_repo.get_watches_to_notify()
        chats_to_send = dict[int, list[CryptoWatch]]()
        watches_to_upsert: list[CryptoWatch] = []

        for watch in watches:
            watch.next_execution_at = WatchInterval.get_next_datetime(watch.interval)

            if watch.tg_chat.tg_id not in chats_to_send:
                chats_to_send[watch.tg_chat.tg_id] = []

            chats_to_send[watch.tg_chat.tg_id].append(watch)

        async with asyncio.TaskGroup() as tg:
            for chat_id, chat_watches in chats_to_send.items():
                self.__logger.info(
                    f'notify: processing chat_id: {chat_id}, number of watches: {len(chat_watches)}')

                async def _(cws: list[CryptoWatch]):
                    try:
                        self.__logger.info(f'notify: sending notification to {chat_id}, watches: {len(cws)}')
                        # print(render_watch_notification_text(cws))
                        await self.__tg_bot.bot.send_message(
                            chat_id=chat_id,
                            text=render_watch_notification_text(cws),
                            disable_web_page_preview=True
                        )
                        self.__logger.info(f'notify: sent notification to {chat_id}, watches: {len(cws)} successfully')
                    except Exception as e:
                        self.__logger.error(
                            f'Failed to send notification for to chat_id: {chat_id}, watches: {len(cws)}: {e}'
                        )

                tg.create_task(_(chat_watches))

        await self.__watches_repo.bulk_upsert(watches_to_upsert)

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
