from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

class NavState(StatesGroup):
    catalog = State()