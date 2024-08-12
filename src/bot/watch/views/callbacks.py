from bot.callbacks import RedisCb


class WatchSelectIntervalCb(RedisCb, prefix='WatchSelectIntervalCb'):
    asset_uuid: str
    tg_user_id: int
    interval: str
