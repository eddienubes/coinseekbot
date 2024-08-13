from bot.callbacks import RedisCb


class AddToFavouritesCb(RedisCb, prefix='AFCb'):
    asset_uuid: str
    tg_user_id: int


class RemoveFromFavouritesCb(RedisCb, prefix='RFCb'):
    asset_uuid: str
    tg_user_id: int
