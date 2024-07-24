import logging

from apscheduler.triggers.calendarinterval import CalendarIntervalTrigger

from config import config
from cron import CronService
from .binance_ingest_service import BinanceIngestService
from .binance_trading_pairs_service import BinanceTradingPairsService


class BinanceCronService:
    def __init__(self,
                 ingest_service: BinanceIngestService,
                 cron_service: CronService,
                 trading_pairs_service: BinanceTradingPairsService
                 ):
        self.__logger = logging.getLogger(BinanceCronService.__name__)
        self.__ingest_service = ingest_service
        self.__trading_pairs_service = trading_pairs_service
        self.__cron_service = cron_service

    async def on_module_init(self):
        if config.env == 'test':
            return

        # Update assets every day at 01:00
        self.__cron_service.add_job(self.__ingest_service.ingest_assets, CalendarIntervalTrigger(hour=1))
        self.__cron_service.add_job(self.__trading_pairs_service.update_trading_pair_price_changes,
                                    CalendarIntervalTrigger(minute=30))
