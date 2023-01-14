from ManagementSystem.ext.models.recover_pw import *
from . import db, MongoDBResult

"""
Это собственно-написанная ORM - для NoSql базы данных MongoDB, для взаимодействия с моделью RecoverPW
Документ: recovers
"""


# получение записей о всех пользователях
def get_recovers() -> MongoDBResult:
    res = db.recovers.find()
    if res:
        recovers = []
        for i in list(res):
            recovers.append(RecoverPW(i))
        return MongoDBResult(True, recovers)
    else:
        return MongoDBResult(False, [])


# проверка запроса на восстановление по ID
def get_recover_by_id(id) -> MongoDBResult:
    res = db.recovers.find_one({'_id': ObjectId(id)})
    if res:
        return MongoDBResult(True, RecoverPW(res))
    else:
        return MongoDBResult(False, None)


# проверка запроса на восстановление по user ID
def get_recover_by_user_id(user_id: str) -> MongoDBResult:
    res = db.recovers.find_one({'user_id': ObjectId(user_id)})
    if res:
        return MongoDBResult(True, RecoverPW(res))
    else:
        return MongoDBResult(False, None)


# проверка запроса на восстановление по номеру телефона
def get_recover_by_phone(phone_number: str) -> MongoDBResult:
    res = db.recovers.find_one({'phone_number': phone_number})
    if res:
        return MongoDBResult(True, RecoverPW(res))
    else:
        return MongoDBResult(False, None)


# добавление пользователя
def add_recover(phone_number: str, user_id: str):
    db.recovers.insert_one({
        "phone_number": phone_number,
        "user_id": ObjectId(user_id)
    })


# добавление пользователей
def add_recovers(recovers):
    db.recovers.insert_many(recovers)


# обновление данных пользователя по ID
def update(id, key, value):
    db.recovers.update_one({'_id': ObjectId(id)}, {"$set": {key: value}})


# удаление запросов по user_id
def delete_recovers_by_user_id(user_id):
    try:
        db.recovers.delete_many({
            'user_id': ObjectId(user_id)
        })
    except Exception as ex:
        print(ex)


# удаление запроса по ID
def delete_recover(id):
    db.recovers.delete_one({
        '_id': ObjectId(id)
    })


# очистка Документа
def truncate():
    db.recovers.drop()
