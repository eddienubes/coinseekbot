from aiogram.filters.callback_data import CallbackData

from bot.callbacks import RedisCb


class WatchlistFavouritesCb(CallbackData, prefix='WLFCb'):
    tg_user_id: int


class WatchlistPageCb(CallbackData, prefix='WLPCb'):
    tg_user_id: int
    offset: int


class WatchSelectIntervalCb(CallbackData, prefix='WFSb'):
    tg_user_id: int
    asset_uuid: str


class StartWatchingCb(RedisCb, prefix='WSICb'):
    tg_user_id: int
    asset_uuid: str
    interval: str


class StopWatchingConfirmationCb(CallbackData, prefix='SWCCb'):
    tg_user_id: int
    asset_uuid: str


class StopWatchingCb(CallbackData, prefix='SWCb'):
    tg_user_id: int
    asset_uuid: str
