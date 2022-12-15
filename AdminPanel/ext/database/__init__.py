from pymongo import MongoClient
from AdminPanel.config import load_config
from dataclasses import dataclass
import logging

config = load_config()  # config
logger = logging.getLogger(__name__)  # logging

db = MongoClient(config.db.conn).jewell  # jewell - название БД

logger.info('Database engine inited')


@dataclass
class MongoDBResult:
    # Класс для возврата данных
    success: bool
    data: ...
