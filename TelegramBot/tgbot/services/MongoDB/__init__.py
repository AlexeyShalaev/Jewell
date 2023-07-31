import logging
from dataclasses import dataclass

from pymongo import MongoClient

from TelegramBot.tgbot.config import load_config

config = load_config()  # config

db = MongoClient(config.db.conn).jewell  # jewell - название БД

logging.info('Database engine inited')


@dataclass
class MongoDBResult:
    # Класс для возврата данных
    success: bool
    data: ...
