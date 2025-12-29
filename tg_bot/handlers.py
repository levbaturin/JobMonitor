from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, BotCommand, BotCommandScopeDefault
from aiogram.filters import CommandStart, Command
from tg_bot.lexicon import LEXICON_RU
from data.database import db

router = Router()

async def set_bot_menu(bot: Bot):
    commands = [
        BotCommand(command="start", description="Начало"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="start_monitoring", description="Начать мониторинг"),
        BotCommand(command="stop_monitoring", description="Закончить мониторинг"),
    ]

    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())

@router.message(CommandStart())
async def cmd_start(message: Message):
    if not message.from_user:
        await message.answer("❌ Ошибка: не удалось получить данные пользователя")
        return

    db.reg_user(message.from_user.id, message.from_user.username)
    message.answer(LEXICON_RU['cmd_start'])

@router.message(Command('help'))
async def cmd_help(message: Message):
    message.answer(LEXICON_RU['cmd_help'])

@router.message(Command('start_monitoring'))
async def cmd_start_monitoring(message: Message):
    if not message.from_user:
        await message.answer("❌ Ошибка: не удалось получить данные пользователя")
        return
    db.add_sub(message.from_user.id)
    message.answer(LEXICON_RU['cmd_start_monitoring'])

@router.message(Command('start_monitoring'))
async def cmd_stop_monitoring(message: Message):
    if not message.from_user:
        await message.answer("❌ Ошибка: не удалось получить данные пользователя")
        return
    db.del_sub(message.from_user.id)
    message.answer(LEXICON_RU['cmd_stop_monitoring'])