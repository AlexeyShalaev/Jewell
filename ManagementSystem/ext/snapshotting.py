import logging
import os
import tarfile
from datetime import datetime

from bson.json_util import dumps, loads
from pymongo import MongoClient

from ManagementSystem.config import load_config

config = load_config()  # config
logger = logging.getLogger(__name__)  # logging
db = MongoClient(config.db.conn).jewell  # jewell - название БД
temporary_folder = '../storage/broker'
database_folder = '../storage/database'
backups_folder = '../storage/backups'


def backup():
    try:
        export_database_to_json()
        archive_data()
    except Exception as ex:
        logger.error(ex)
    clear_temporary_folder()


def restore(filename: str):
    try:
        # todo auto find latest
        extract_data_from_backup(filename)
        export_database_to_json()
    except Exception as ex:
        logger.error(ex)
    clear_temporary_folder()


def extract_data_from_backup(filename):
    file = tarfile.open(f'{backups_folder}/{filename}.tar.gz')
    # file.extract() todo
    file.close()


def export_database_to_json():
    for collection_name in db.list_collection_names():
        collection = db[collection_name]
        data = list(collection.find())
        json_data = dumps(data)
        with open(f'{temporary_folder}/{collection_name}.json', 'w') as file:
            file.write(json_data)


def archive_data():
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    with tarfile.open(f'{backups_folder}/database-{timestamp}.tar.gz', "w:gz") as tar:
        tar.add(temporary_folder)
        tar.add(database_folder)


def clear_temporary_folder():
    try:
        for file in os.listdir(temporary_folder):
            os.remove(os.path.join(temporary_folder, file))
    except Exception as ex:
        logger.error(ex)


def import_database_from_json():
    try:
        files = os.listdir(temporary_folder)
        for file in files:
            with open(os.path.join(temporary_folder, file)) as f:
                file_data = loads(f.read())
                index = file.rfind('.')
                collection_name = file[:index]
                db[collection_name].drop()
                db[collection_name].insert_many(file_data)
    except Exception as ex:
        logger.error(ex)
