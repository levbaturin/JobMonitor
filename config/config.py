import os
import logging
from dotenv import load_dotenv
from dataclasses import dataclass
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN', '')
VK_TOKEN = os.getenv('VK_TOKEN', '')
BOT_OWNER_ID = int(os.getenv('BOT_OWNER_ID', ''))
TG_API_ID= int(os.getenv('TG_API_ID', ''))
TG_API_HASH=os.getenv('TG_API_HASH', '')

@dataclass
class LogSettings:
    name: str
    dir: str
    filename: str
    size: int
    backup_count: int
    level: int
    format: str

@dataclass
class LogFilterSettings:
    name: str
    dir: str
    filename: str
    size: int
    backup_count: int
    level: int
    format: str

@dataclass
class DataBaseSettings:
    path: str

@dataclass
class TgBot:
    token: str
    owner_id: int
    default: DefaultBotProperties

@dataclass
class VKParser:
    token: str
    vk_api_version: str

@dataclass
class TgAPI:
    id: int
    hash: str
    token: str


def load_log_settings():
    return LogSettings(
        name='app',
        dir='logs',
        filename='app.log',
        size=5 * 1024 * 1024,
        backup_count=3,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(message)s | (%(filename)s:%(lineno)d)"
        )

def load_log_filter_settings():
    return LogFilterSettings(
        name='filter_log',
        dir='logs',
        filename='filtrated.log',
        size=5 * 1024 * 1024,
        backup_count=3,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
        )

def load_db_settings():
    return DataBaseSettings(
        path='data/data.db',
        )

def load_bot_settings():
    return TgBot(
        token=BOT_TOKEN,
        owner_id=BOT_OWNER_ID,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

def load_vk_settings():
    return VKParser(
        token=VK_TOKEN,
        vk_api_version='5.131'
    )

def load_tg_api_settings():
    return TgAPI(
        id=TG_API_ID,
        hash=TG_API_HASH,
        token=BOT_TOKEN
    )