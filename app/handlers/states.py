from aiogram.fsm.state import State, StatesGroup


class FilterInputState(StatesGroup):
    waiting_city = State()
    waiting_city_pick = State()
    waiting_text = State()
    waiting_salary = State()
