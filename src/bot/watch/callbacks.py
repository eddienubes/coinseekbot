from aiogram.filters.callback_data import CallbackData


class WatchCallback(CallbackData, prefix='watch'):
    asset_uuid: str
    tg_user_id: int
