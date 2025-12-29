from aiogram.fsm.state import State, StatesGroup

class AddGroupStates(StatesGroup):
    waiting_for_group_url = State()