import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Bot, Dispatcher
from config.config import TgBot, load_bot_settings
from tg_bot.handlers import router
from logs.logger import logger
from data.database import db

bot_set: TgBot = load_bot_settings()

async def main():
    bot= Bot(token=bot_set.token, default=bot_set.default)

    dp = Dispatcher()
    dp.include_router(router)

    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        ...
    )

    scheduler.start()

    logger.info("Бот запущен")

    try:
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown()
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())