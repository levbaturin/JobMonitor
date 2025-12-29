from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, BotCommand, BotCommandScopeDefault
from aiogram.filters import CommandStart, Command
from tg_bot.lexicon import LEXICON_RU
from data.database import db
from logs.logger import logger
from tg_bot.filters import IsAdminFilter
from aiogram.fsm.context import FSMContext
from tg_bot.states import AddGroupStates

admin_router = Router()

admin_router.message.filter(IsAdminFilter())

async def set_admin_bot_menu(bot: Bot):
    commands = [
            BotCommand(command="start", description="Начало"),
            BotCommand(command="help", description="Помощь"),
            BotCommand(command="start_monitoring", description="Начать мониторинг"),
            BotCommand(command="stop_monitoring", description="Закончить мониторинг"),
            BotCommand(command="add_group", description="Добавить группу"),
            BotCommand(command="del_group", description="Удалить группу"),
        ]

    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())

@admin_router.message(Command('add_group'))
async def cmd_add_group(message: Message, state: FSMContext) -> None:
    await state.set_state(AddGroupStates.waiting_for_group_url)
    await message.answer(
        "📝 Отправьте ссылку на группу:\n\n"
        "Примеры:\n"
        "• https://vk.com/club123456\n"
        "• https://vk.com/public789456"
    )

@admin_router.message(AddGroupStates.waiting_for_group_url)
async def process_group_url(message: Message, state: FSMContext) -> None:
    ...