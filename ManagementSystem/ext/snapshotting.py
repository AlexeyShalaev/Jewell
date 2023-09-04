import logging
import os
import re
import tarfile
from datetime import datetime

from bson.json_util import dumps, loads
from pymongo import MongoClient

from ManagementSystem.config import load_config

config = load_config()  # config

db = MongoClient(config.db.conn).jewell  # jewell - название БД

temporary_folder = 'storage/broker'
database_folder = 'storage/database'
backups_folder = 'storage/backups'

backup_time_format = '%Y-%m-%d-%H-%M-%S'


def check_content(file: str) -> bool:
    try:
        database_folder_flag = False
        tar = tarfile.open(file)
        for name in tar.getnames():
            if '.' not in name:
                if name == 'database':
                    database_folder_flag = True
            else:
                if name.endswith('.json'):
                    index = name.rfind('.')
                    collection_name = name[:index]
                    if collection_name not in db.list_collection_names():
                        tar.close()
                        return False
        tar.close()
        return database_folder_flag
    except Exception as ex:
        logging.error(ex)
        return False


def check_filename(filename):
    return re.fullmatch(r'\w+-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}\.tar\.gz', filename)


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


def backup() -> (bool, str):
    filename = ''
    clear_temporary_folder()
    try:
        export_database_to_json()
        filename = archive_data()
    except Exception as ex:
        logging.error(ex)
        return False, None
    clear_temporary_folder()
    return True, filename


def restore(filename: str = 'latest') -> bool:
    clear_temporary_folder()
    try:
        status, filename = get_backup_filename(filename)
        if not status:
            return False
        extract_data_from_backup(filename)
        import_database_from_json()
    except Exception as ex:
        logging.error(ex)
        return False
    clear_temporary_folder()
    return True


def archive_data() -> str:
    timestamp = datetime.now().strftime(backup_time_format)
    filename = f'{backups_folder}/database-{timestamp}.tar.gz'
    with tarfile.open(filename, "w:gz") as tar:
        tar.add(temporary_folder, arcname="")
        tar.add(database_folder, arcname=database_folder.split('/')[1])
    return filename


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
            try:
                with open(os.path.join(temporary_folder, file)) as f:
                    file_data = loads(f.read())
                    index = file.rfind('.')
                    collection_name = file[:index]
                    db[collection_name].drop()
                    db[collection_name].insert_many(file_data)
            except:
                pass
    except Exception as ex:
        logging.error(ex)


def clear_temporary_folder():
    try:
        for file in os.listdir(temporary_folder):
            os.remove(os.path.join(temporary_folder, file))
    except Exception as ex:
        logging.error(ex)
