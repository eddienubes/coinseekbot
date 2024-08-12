from bot.callbacks import RedisCb


class WatchCb(RedisCb, prefix='WatchCb'):
    asset_uuid: str
    tg_user_id: int
    interval: str
