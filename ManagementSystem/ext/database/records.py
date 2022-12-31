from . import db, MongoDBResult
from ManagementSystem.ext.models.record import *

"""
Это собственно-написанная ORM - для NoSql базы данных MongoDB, для взаимодействия с моделью Record
Документ: records
"""


# получение всех записей
def get_records() -> MongoDBResult:
    res = db.records.find()
    if res:
        records = []
        for i in list(res):
            records.append(Record(i))
        return MongoDBResult(True, records)
    else:
        return MongoDBResult(False, [])


# получение записей по автору
def get_records_by_author(author) -> MongoDBResult:
    res = db.records.find({'author': ObjectId(author)})
    if res:
        records = []
        for i in list(res):
            records.append(Record(i))
        return MongoDBResult(True, records)
    else:
        return MongoDBResult(False, [])


# получение записей по типу
def get_records_by_type(type: RecordType) -> MongoDBResult:
    res = db.records.find({'type': type.value})
    if res:
        records = []
        for i in list(res):
            records.append(Record(i))
        return MongoDBResult(True, records)
    else:
        return MongoDBResult(False, [])


# получение записи по ID
def get_record_by_id(id) -> MongoDBResult:
    record = db.records.find_one({'_id': ObjectId(id)})
    if record:
        # пользователь существует
        return MongoDBResult(True, Record(record))
    else:
        # пользователя нет
        return MongoDBResult(False, None)


# добавление записи
def add_record(author, text, time, type=RecordType.POST):
    db.records.insert_one({
        "author": ObjectId(author),
        "type": type.value,
        "text": text,
        "time": time,
    })


# добавление записей
def add_records(records):
    db.records.insert_many(records)


# обновление данных записи по ID
def update_record(id, key, value):
    db.records.update_one({'_id': ObjectId(id)}, {"$set": {key: value}})


# удаление записи по ID
def delete_record(id):
    db.records.delete_one({
        '_id': ObjectId(id)
    })


# очистка Документа
def truncate():
    db.records.drop()
