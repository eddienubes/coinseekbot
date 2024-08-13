from aiogram.fsm.state import StatesGroup, State


class WatchMenuState(StatesGroup):
    SHOW_FAVOURITES = State()
    SELECT_INTERVAL = State()
    CONFIRMATION = State()
