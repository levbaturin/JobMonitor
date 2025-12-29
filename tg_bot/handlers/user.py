from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, BotCommand, BotCommandScopeDefault
from aiogram.filters import CommandStart, Command
from tg_bot.lexicon import LEXICON_RU
from data.database import db
from logs.logger import logger

user_router = Router()

async def set_user_bot_menu(bot: Bot):
    commands = [
        BotCommand(command="start", description="Начало"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="start_monitoring", description="Начать мониторинг"),
        BotCommand(command="stop_monitoring", description="Закончить мониторинг"),
    ]

    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())

@user_router.message(CommandStart())
async def cmd_start(message: Message):
    if not message.from_user:
        await message.answer("❌ Ошибка: не удалось получить данные пользователя")
        return

    db.reg_user(message.from_user.id, message.from_user.username)
    logger.info(f'Зарегистрирован новый пользователь {message.from_user.username} с id {message.from_user.id}')
    await message.answer(LEXICON_RU['cmd_start'])

@user_router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer(LEXICON_RU['cmd_help'])

@user_router.message(Command('start_monitoring'))
async def cmd_start_monitoring(message: Message):
    if not message.from_user:
        await message.answer("❌ Ошибка: не удалось получить данные пользователя")
        return
    db.add_sub(message.from_user.id)
    logger.info(f'На мониторинг подписался пользователь {message.from_user.username} с id {message.from_user.id}')
    await message.answer(LEXICON_RU['cmd_start_monitoring'])

@user_router.message(Command('stop_monitoring'))
async def cmd_stop_monitoring(message: Message):
    if not message.from_user:
        await message.answer("❌ Ошибка: не удалось получить данные пользователя")
        return
    db.del_sub(message.from_user.id)
    logger.info(f'С мониторинга отписался пользователь {message.from_user.username} с id {message.from_user.id}')
    await message.answer(LEXICON_RU['cmd_stop_monitoring'])