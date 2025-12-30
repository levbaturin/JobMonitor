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

# Применить фильтр для всех сообщений в router
admin_router.message.filter(IsAdminFilter())


async def set_admin_bot_menu(bot: Bot, admin_id: int):
    """Установить меню команд для администратора"""

    commands = [
        BotCommand(command="start", description="Начало"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="start_monitoring", description="Начать мониторинг"),
        BotCommand(command="stop_monitoring", description="Закончить мониторинг"),
        BotCommand(command="add_groups", description="Добавить группы VK"),
        BotCommand(command="del_groups", description="Удалить группы"),
    ]

    await bot.set_my_commands(commands, scope=BotCommandScopeChat(chat_id=admin_id))


@admin_router.message(Command('add_groups'))
async def cmd_add_groups(message: Message, state: FSMContext) -> None:
    """Команда добавления групп VK"""

    await state.set_state(AddGroupStates.waiting_for_group_url)
    await message.answer(
        text="<b>📝 Добавление групп VK</b>\n\n"
        "Отправьте ссылки на группы VK (по одной на строку):\n\n"
        "Примеры:\n"
        "🔹 <code>https://vk.com/vacancies_kras</code>\n"
        "🔹 <code>vk.com/job_russia</code>\n"
        "🔹 <code>vacancies_spb</code>\n\n"
        "Можешь отправить несколько ссылок сразу (каждую на новой строке)",
        parse_mode="HTML",
        disable_web_page_preview=True
    )


@admin_router.message(AddGroupStates.waiting_for_group_url)
async def process_group_urls(message: Message, state: FSMContext) -> None:
    """Обработка ссылок на группы VK"""

    if not message.text:
        await message.answer("❌ Отправьте ссылки на группы")
        return

    processing_msg = await message.answer("⏳ Обрабатываю...")

    urls = [url.strip() for url in message.text.strip().split('\n') if url.strip()]

    added = []
    failed = []

    for url in urls:
        try:
            # Получить информацию о группе VK
            group_info = await get_vk_group_info(url)

            # Проверить что функция вернула корректные данные
            if not group_info or 'id' not in group_info:
                failed.append(f"❌ {url} - Не удалось получить информацию")
                logger.warning(f"[VK] Не удалось получить инфо: {url}")
                continue

            group_id = group_info['id']
            title = group_info.get('name') or group_info.get('title', 'Unknown')

            if not title:
                failed.append(f"❌ {url} - Не получилось имя группы")
                logger.warning(f"[VK] {group_id} - нет названия")
                continue

            # Проверить наличие в БД
            if db.group_exists(group_id, source='vk'):
                failed.append(f"❌ {title} - уже добавлена")
                logger.warning(f"[VK] {group_id} уже в БД")
                continue

            # Добавить в БД
            db.reg_group(group_id=group_id, title=title, source='vk')
            added.append(f"✅ {title}")
            logger.info(f"[VK] ✅ Добавлена: {title} ({group_id})")

        except Exception as e:
            failed.append(f"❌ {url} - {str(e)}")
            logger.error(f"[VK] Ошибка обработки {url}: {e}")

    await processing_msg.delete()

    # Формируем результат
    result = "<b>📊 Результат добавления</b>\n\n"

    if added:
        result += f"<b>✅ Добавлено ({len(added)}):</b>\n"
        result += "\n".join(added)

    if failed:
        if added:
            result += "\n\n"
        result += f"<b>❌ Ошибки ({len(failed)}):</b>\n"
        result += "\n".join(failed)

    if not added and not failed:
        result = "❌ Ничего не добавлено"

    await message.answer(result, parse_mode="HTML")
    await state.clear()


@admin_router.message(Command('del_groups'))
async def cmd_del_groups(message: Message, state: FSMContext) -> None:
    """Команда удаления групп VK"""

    groups = db.get_all_active_groups()

    if not groups:
        await message.answer("❌ Групп VK не найдено")
        return

    text = "<b>📋 Существующие группы VK:</b>\n\n"

    for group in groups:
        group_id = group['group_id']
        title = group['title']
        text += f"🔹 <b>{title}</b>\n   ID: <code>{group_id}</code>\n\n"

    text += "<b>📝 Отправьте ID группы для удаления</b> (или несколько через запятую или пробел)\n"
    text += "Пример: <code>234935586, 123456789</code>"

    await message.answer(text, parse_mode="HTML")
    await state.set_state(AddGroupStates.waiting_for_delete)


@admin_router.message(AddGroupStates.waiting_for_delete)
async def process_delete_groups(message: Message, state: FSMContext) -> None:
    """Удаление групп VK"""

    if not message.text:
        await message.answer("❌ Отправьте ID выбранных групп")
        return

    # Парсим ID (могут быть с запятыми или пробелами)
    ids = [
        id_str.strip()
        for id_str in message.text.replace(',', ' ').split()
        if id_str.strip().lstrip('-').isdigit()
    ]

    if not ids:
        await message.answer("❌ ID не найдены")
        return

    deleted = []
    failed = []

    for group_id in ids:
        try:
            group_id_int = int(group_id)

            # Проверяем наличие в БД (только VK)
            if db.group_exists(group_id_int, source='vk'):
                db.delete_group(group_id_int, source='vk')
                deleted.append(f"✅ Группа {group_id_int} удалена")
                logger.info(f"[VK] ✅ Группа {group_id_int} удалена")
            else:
                failed.append(f"❌ Группа {group_id_int} не найдена")
                logger.warning(f"[VK] Группа {group_id_int} не найдена в БД")

        except Exception as e:
            failed.append(f"❌ {group_id} - {str(e)}")
            logger.error(f"[VK] Ошибка удаления {group_id}: {e}")

    # Формируем результат
    result = "<b>📊 Результат удаления</b>\n\n"

    if deleted:
        result += f"<b>✅ Удалено ({len(deleted)}):</b>\n"
        result += "\n".join(deleted)

    if failed:
        if deleted:
            result += "\n\n"
        result += f"<b>❌ Ошибки ({len(failed)}):</b>\n"
        result += "\n".join(failed)

    if not deleted and not failed:
        result = "❌ Ничего не удалено"

    await message.answer(result, parse_mode="HTML")
    await state.clear()
