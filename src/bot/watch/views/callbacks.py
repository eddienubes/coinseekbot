from sys import prefix

from aiogram.filters.callback_data import CallbackData

from bot.callbacks import RedisCb, BaseCb


class WatchlistFavouritesCb(BaseCb, prefix='WLFCb'):
    pass


class WatchlistPageCb(BaseCb, prefix='WLPCb'):
    offset: int


class WatchSelectIntervalCb(BaseCb, prefix='WFSb'):
    asset_uuid: str


class StartWatchingCb(RedisCb, prefix='WSICb'):
    asset_uuid: str
    interval: str


class StopWatchingConfirmationCb(BaseCb, prefix='SWCCb'):
    asset_uuid: str


class StopWatchingCb(BaseCb, prefix='SWCb'):
    asset_uuid: str
