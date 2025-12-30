from aiogram import Router, Bot, F
from aiogram.types import Message, BotCommand, BotCommandScopeChat
from aiogram.filters import Command
from data.database import db
from logs.logger import logger
from aiogram.fsm.context import FSMContext
from tg_bot.states import AddGroupStates
from config.config import load_bot_settings, TgBot

owner_router = Router()

bot_set: TgBot = load_bot_settings()

owner_router.message.filter(F.from_user.id == bot_set.owner_id)

async def set_owner_bot_menu(bot: Bot, owner_id: int):
    """Установить меню команд для владельца бота."""

    commands = [
            BotCommand(command="start", description="Начало"),
            BotCommand(command="help", description="Помощь"),
            BotCommand(command="start_monitoring", description="Начать мониторинг"),
            BotCommand(command="stop_monitoring", description="Закончить мониторинг"),
            BotCommand(command="add_groups", description="Добавить группы"),
            BotCommand(command="del_groups", description="Удалить группы"),
            BotCommand(command="add_admin", description="Добавить админа"),
            BotCommand(command="del_admin", description="Удалить админа"),
        ]

    await bot.set_my_commands(commands, scope=BotCommandScopeChat(chat_id=owner_id))

@owner_router.message(Command('add_admin'))
async def cmd_add_admin(message: Message, state: FSMContext):
    """Запросить у владельца id для добавления администратора."""

    await message.answer(text='Введите id: ')
    await state.set_state(AddGroupStates.waiting_for_admin_id)

@owner_router.message(AddGroupStates.waiting_for_admin_id)
async def process_adding_admin(message: Message, state: FSMContext) -> None:
    """Обработать добавление администратора по введённому id."""

    if not message.text:
        await message.answer("❌ Отправьте id аккаунта Telegram")
        return

    processing_msg = await message.answer("⏳ Обрабатываю...")

    try:
        admin_id = int(message.text.strip())
    except ValueError:
        await processing_msg.delete()
        await message.answer("❌ ID должен быть числом")
        await state.clear()
        return

    if db.check_is_admin(admin_id):
        await processing_msg.delete()
        await message.answer(f"❌ Пользователь {admin_id} уже администратор")
        await state.clear()
        return

    try:
        db.add_admin(admin_id)

        await processing_msg.delete()
        await message.answer(f"✅ Администратор {admin_id} добавлен успешно")
        logger.info(f'Добавлен новый администратор {admin_id}')

    except Exception as e:
        await processing_msg.delete()
        await message.answer(f"❌ Ошибка: {str(e)}")
        logger.error(f'Ошибка при добавлении админа: {str(e)}')

    await state.clear()

@owner_router.message(Command('del_admin'))
async def cmd_del_admin(message: Message, state: FSMContext):
    """Запросить id администратора для удаления."""

    await message.answer(text='Введите id администратора для удаления: ')
    await state.set_state(AddGroupStates.waiting_for_delete_admin_id)


@owner_router.message(AddGroupStates.waiting_for_delete_admin_id)
async def process_deleting_admin(message: Message, state: FSMContext) -> None:
    """Обработать удаление администратора по введённому id."""

    if not message.text:
        await message.answer("❌ Отправьте id аккаунта Telegram")
        await state.clear()
        return

    processing_msg = await message.answer("⏳ Обрабатываю...")

    try:
        admin_id = int(message.text.strip())
    except ValueError:
        await processing_msg.delete()
        await message.answer("❌ ID должен быть числом")
        await state.clear()
        return

    if not db.check_is_admin(admin_id):
        await processing_msg.delete()
        await message.answer(f"❌ Пользователь {admin_id} не является администратором")
        await state.clear()
        return

    if admin_id == bot_set.owner_id:
        await processing_msg.delete()
        await message.answer("❌ Нельзя удалить владельца бота")
        await state.clear()
        return

    try:
        db.del_admin(admin_id)

        await processing_msg.delete()
        await message.answer(f"✅ Администратор {admin_id} удален успешно")
        logger.info(f'Удален администратор {admin_id}')

    except Exception as e:
        await processing_msg.delete()
        await message.answer(f"❌ Ошибка: {str(e)}")
        logger.error(f'Ошибка при удалении админа: {str(e)}')

    await state.clear()
