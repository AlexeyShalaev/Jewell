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

temporary_folder = 'storage/broker'
database_folder = 'storage/database'
backups_folder = 'storage/backups'

backup_time_format = '%Y-%m-%d-%H-%M-%S'


def get_backup_date(filename: str) -> datetime:
    start = filename.find('-')
    end = filename.find('.tar')
    timestamp = filename[start + 1:end]
    return datetime.strptime(timestamp, backup_time_format)


def get_sorted_backups() -> list:
    files = os.listdir(backups_folder)
    if len(files) > 0:
        files.sort(key=get_backup_date, reverse=True)
    return files


def get_backup_filename(filename: str) -> (bool, str):
    if filename == 'latest':
        files = get_sorted_backups()
        if len(files) == 0:
            return False, None
        filename = files[0]
    else:
        if not filename.endswith('.tar.gz'):
            filename += '.tar.gz'
        if not os.path.exists(f'{backups_folder}/{filename}'):
            return False, None
    return True, filename


def backup() -> bool:
    try:
        export_database_to_json()
        archive_data()
    except Exception as ex:
        logger.error(ex)
        return False
    clear_temporary_folder()
    return True


def restore(filename: str = 'latest') -> bool:
    try:
        status, filename = get_backup_filename(filename)
        if not status:
            return False
        extract_data_from_backup(filename)
        import_database_from_json()
    except Exception as ex:
        logger.error(ex)
        return False
    clear_temporary_folder()
    return True


def archive_data():
    timestamp = datetime.now().strftime(backup_time_format)
    with tarfile.open(f'{backups_folder}/database-{timestamp}.tar.gz', "w:gz") as tar:
        tar.add(temporary_folder, arcname="")
        tar.add(database_folder, arcname=database_folder.split('/')[1])


def extract_data_from_backup(filename):
    tar = tarfile.open(f'{backups_folder}/{filename}')
    for member in tar.getmembers():
        if member.path.endswith('.json'):
            tar.extract(member, temporary_folder)
        elif member.path.startswith(database_folder.split('/')[1]):
            tar.extract(member, 'storage')
    tar.close()


def export_database_to_json():
    for collection_name in db.list_collection_names():
        collection = db[collection_name]
        data = list(collection.find())
        json_data = dumps(data)
        with open(f'{temporary_folder}/{collection_name}.json', 'w') as file:
            file.write(json_data)


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


def clear_temporary_folder():
    try:
        for file in os.listdir(temporary_folder):
            os.remove(os.path.join(temporary_folder, file))
    except Exception as ex:
        logger.error(ex)
