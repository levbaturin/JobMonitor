import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Bot, Dispatcher
from config.config import TgBot, load_bot_settings
from tg_bot.handlers.user import user_router, set_user_bot_menu
from tg_bot.handlers.admin import admin_router, set_admin_bot_menu
from logs.logger import logger
from data.database import db
from utils.check_and_send import check_and_send
from tg_bot.handlers.owner import owner_router, set_owner_bot_menu

bot_set: TgBot = load_bot_settings()

async def main():
    bot= Bot(token=bot_set.token, default=bot_set.default)

    dp = Dispatcher()
    dp.include_router(owner_router)
    dp.include_router(admin_router)
    dp.include_router(user_router)

    admin_ids = db.get_all_admins()

    await set_owner_bot_menu(bot, bot_set.owner_id)

    for admin_id in admin_ids:
        await set_admin_bot_menu(bot, admin_id)

    db.add_admin(bot_set.owner_id)

    await set_user_bot_menu(bot)

    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        check_and_send,
        'interval',
        seconds=15,
        args=[bot],
        id='job_parser'
    )

    scheduler.start()

    logger.info("Бот запущен")

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        scheduler.shutdown()
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())