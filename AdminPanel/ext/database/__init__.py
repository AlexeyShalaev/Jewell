from pymongo import MongoClient
from bunnet import init_bunnet
from AdminPanel.ext.models.jewell import *
from ...config import load_config
import logging

config = load_config()  # config
logger = logging.getLogger(__name__)  # logging

client = MongoClient(config.db.conn)  # pymongo client

init_bunnet(database=client.jewell, document_models=[User])  # https://github.com/roman-right/bunnet

logger.info('Database engine inited')
