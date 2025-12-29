import logging
import logging.handlers
from pathlib import Path
from config.config import load_log_settings, load_log_filter_settings, LogSettings, LogFilterSettings

log: LogSettings = load_log_settings()
log_filter: LogFilterSettings = load_log_filter_settings()

LOG_DIR = Path(log.dir)
LOG_DIR.mkdir(exist_ok=True)

def setup_logger(name: str = 'app'):
    logger = logging.getLogger(name)
    logger.setLevel(log.level)

    if logger.hasHandlers():
        return logger

    formatter = logging.Formatter(fmt=log.format)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log.level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.handlers.RotatingFileHandler(
        filename=LOG_DIR / log.filename,
        maxBytes=log.size,
        backupCount=log.backup_count,
        encoding='utf-8'
    )

    file_handler.setLevel(log.level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

def setup_filter_logger(name: str = log_filter.name):
    filter_logger = logging.getLogger(name)
    filter_logger.setLevel(log_filter.level)

    if filter_logger.hasHandlers():
        return filter_logger


    formatter = logging.Formatter(fmt=log_filter.format)

    file_handler = logging.handlers.RotatingFileHandler(
        filename=LOG_DIR / log_filter.filename,
        maxBytes=log_filter.size,
        backupCount=log_filter.backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    filter_logger.addHandler(file_handler)

    return filter_logger

logger = setup_logger(log.name)
filter_logger = setup_filter_logger(log_filter.name)
