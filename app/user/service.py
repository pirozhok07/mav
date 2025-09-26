from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Filter
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from loguru import logger

class NavState(StatesGroup):
    catalog = State()
    
class CallbackStateFilter(Filter):
    def __init__(self, data_pattern: str = None, state:str = None):
        self.data_pattern = data_pattern
        self.state=state

    async def __call__(self, callback: CallbackQuery, state: FSMContext) -> bool:
        logger.error(callback.data)
        logger.error(state.get_state())
        if self.data_pattern:
            if not callback.data.startswith(self.data_pattern):
                return False
        if self.state:
            current_state = await state.get_state()
            if current_state != self.state:
                return False
        return True


