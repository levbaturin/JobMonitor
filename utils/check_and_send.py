from data.database import db
from parsing.vk_parser import parse_all_vk_groups
from logs.logger import logger
from aiogram import Bot
from html import escape
import asyncio

async def check_and_send(bot: Bot) -> None:
    all_jobs = await parse_all_vk_groups()
    if not all_jobs:
        logger.info('Новых объявлений не найдено')
        return

    all_subs_ids = db.get_all_subs_ids()

    for job in all_jobs:
        text = (
    "<b>Новое объявление!</b>\n\n"
    f"{escape(job.text)}\n\n"
    f"<a href='{escape(job.url)}'>Открыть</a>"
)

        for sub_id in all_subs_ids:
            try:
                await bot.send_message(chat_id=sub_id, text=text, disable_web_page_preview=True)
                await asyncio.sleep(0.05)
            except Exception as e:
                logger.error(f"Не удалось отправить юзеру {sub_id}: {e}")
    logger.info(f"✅ Отправлено {len(all_jobs)} вакансий {len(all_subs_ids)} подписчикам")