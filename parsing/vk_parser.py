import aiohttp
import asyncio
from typing import Optional, List
from logs.logger import logger
from config.config import load_vk_settings, VKParser
from parsing.models import Job
from parsing.filters import job_filter
from data.database import db


vk_set : VKParser = load_vk_settings()

async def _parse_vk_group(
    group_id: int,
    last_post_id: Optional[int],
) -> Optional[Job]:
    try:
        params = {
            'owner_id': -abs(int(group_id)),
            'count': 11,
            'filter': 'owner',
            'access_token': vk_set.token,
            'v': vk_set.vk_api_version
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                'https://api.vk.com/method/wall.get',
                params=params,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                data = await response.json()

        posts = data.get('response', {}).get('items', [])

        if not posts:
            return

        post = None

        for pst in posts:
            if pst.get('is_pinned') is False:
                post = pst
                break

        if not post:
            return

        post_id = post.get('id')

        if post_id <= last_post_id and last_post_id != 0:
            return

        db.set_last_post_id(group_id=group_id, last_post_id=post_id)

        owner_id = post.get('owner_id', -abs(int(group_id)))
        url = f"https://vk.com/wall{owner_id}_{post_id}"
        text = post.get('text', '[Нет текста]')

        if text != '[Нет текста]' and not job_filter(text, url):
            return

        job = Job(text=text, url=url)
        logger.info(f"[{group_id}] Новая вакансия: {url}")
        return job

    except Exception as e:
        logger.error(f"[{group_id}] Ошибка: {e}")
        return

async def parse_all_vk_groups() -> List[Job]:
    data = db.get_all_group_ids()
    tasks = [_parse_vk_group(group_id, last_post_id) for group_id, last_post_id in data]
    raw_jobs = await asyncio.gather(*tasks)
    result = [job for job in raw_jobs if job]

    return result
