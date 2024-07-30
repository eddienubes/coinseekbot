from aiogram.filters.callback_data import CallbackData


class DummyCallback(CallbackData, prefix='dummy'):
    pass
