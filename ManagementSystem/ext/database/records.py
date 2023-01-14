from ManagementSystem.ext.models.record import *
from . import db, MongoDBResult

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
def add_record(author, text, time, type=RecordType.POST, lifetime=0):
    return db.records.insert_one({
        "author": ObjectId(author),
        "type": type.value,
        "text": text,
        "time": time,
        "lifetime": lifetime,
    })


# добавление записей
def add_records(records):
    db.records.insert_many(records)


# обновление данных записи по ID
def update_record(id, key, value):
    db.records.update_one({'_id': ObjectId(id)}, {"$set": {key: value}})


# обновление данных записи по ID
def update_record_news(id, text, lifetime):
    db.records.update_one({'_id': ObjectId(id)}, {"$set": {
        "text": text,
        "lifetime": lifetime
    }})


# удаление записей по user_id
def delete_records_by_user_id(user_id):
    try:
        db.records.delete_many({
            'author': ObjectId(user_id)
        })
    except Exception as ex:
        print(ex)


# удаление записи по ID
def delete_record(id):
    db.records.delete_one({
        '_id': ObjectId(id)
    })


# очистка Документа
def truncate():
    db.records.drop()
