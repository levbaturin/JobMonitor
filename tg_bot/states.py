from aiogram.fsm.state import State, StatesGroup

class AddGroupStates(StatesGroup):
    waiting_for_group_url = State()
    waiting_for_delete = State()
    waiting_for_admin_id = State()
    waiting_for_delete_admin_id = State()