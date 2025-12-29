from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, BotCommand, BotCommandScopeDefault, BotCommandScopeChat
from aiogram.filters import CommandStart, Command
from tg_bot.lexicon import LEXICON_RU
from data.database import db
from logs.logger import logger
from tg_bot.filters import IsAdminFilter
from aiogram.fsm.context import FSMContext
from tg_bot.states import AddGroupStates
from parsing.vk_parser import get_vk_group_info

admin_router = Router()

admin_router.message.filter(IsAdminFilter())

async def set_admin_bot_menu(bot: Bot, admin_id: int):
    commands = [
            BotCommand(command="start", description="Начало"),
            BotCommand(command="help", description="Помощь"),
            BotCommand(command="start_monitoring", description="Начать мониторинг"),
            BotCommand(command="stop_monitoring", description="Закончить мониторинг"),
            BotCommand(command="add_groups", description="Добавить группы"),
            BotCommand(command="del_groups", description="Удалить группы"),
        ]

    await bot.set_my_commands(commands, scope=BotCommandScopeChat(chat_id=admin_id))

@admin_router.message(Command('add_groups'))
async def cmd_add_groups(message: Message, state: FSMContext) -> None:
    await state.set_state(AddGroupStates.waiting_for_group_url)
    await message.answer(text=LEXICON_RU['cmd_add_groups'], disable_web_page_preview=True)

@admin_router.message(AddGroupStates.waiting_for_group_url)
async def process_group_urls(message: Message, state: FSMContext) -> None:

    if not message.text:
        await message.answer("❌ Отправьте ссылки")
        return

    processing_msg = await message.answer("⏳ Обрабатываю...")

    urls = [url.strip() for url in message.text.strip().split('\n') if url.strip()]

    added = []
    failed = []

    for url in urls:
        try:
            group_info = await get_vk_group_info(url)

            if db.group_exists(group_info['id']):
                failed.append(f"❌ {url} - уже добавлена")
                continue

            db.reg_group(group_id=group_info['id'], title=group_info['name'])
            added.append(f"✅ {group_info['name']}")

        except Exception as e:
            failed.append(f"❌ {url} - {str(e)}")

    await processing_msg.delete()

    result = "<b>📊 Результат</b>\n\n"
    if added:
        result += "<b>✅ Добавлено:</b>\n" + "\n".join(added) + "\n\n"
    if failed:
        result += "<b>❌ Ошибки:</b>\n" + "\n".join(failed)

    await message.answer(result)
    await state.clear()

@admin_router.message(Command('del_groups'))
async def cmd_del_groups(message: Message, state: FSMContext) -> None:
    groups = db.get_all_active_groups()

    if not groups:
        await message.answer("❌ Групп не найдено")
        return

    text = "📋 Существующие группы:\n\n"
    for group_id, title in groups:
        text += f"🔹 {title} (ID: {group_id})\n"

    text += "\n📝 Отправьте ID группы для удаления (или несколько через запятую)\n"
    text += "Пример: 123456, 789456"

    await message.answer(text)
    await state.set_state(AddGroupStates.waiting_for_delete)

@admin_router.message(AddGroupStates.waiting_for_delete)
async def process_delete_groups(message: Message, state: FSMContext) -> None:

    if not message.text:
        await message.answer("❌ Отправьте id выбранных групп")
        return

    ids = [id_str.strip() for id_str in message.text.replace(',', ' ').split() if id_str.strip().isdigit()]

    if not ids:
        await message.answer("❌ ID не найдены")
        return

    deleted = []
    failed = []

    for group_id in ids:
        try:
            group_id_int = int(group_id)
            if db.group_exists(group_id_int):
                db.delete_group(group_id_int)
                deleted.append(f"✅ Группа {group_id_int} удалена")
            else:
                failed.append(f"❌ Группа {group_id_int} не найдена")
        except Exception as e:
            failed.append(f"❌ {group_id} - {str(e)}")

    result = ""
    if deleted:
        result += "\n".join(deleted)
    if failed:
        result += "\n" + "\n".join(failed)

    await message.answer(result or "Ничего не удалено")
    await state.clear()
