from . import db, MongoDBResult
from AdminPanel.ext.models.userModel import *

"""
Это собственно-написанная ORM - для NoSql базы данных MongoDB, для взаимодействия с моделью User
Документ: users
"""


# проверка пользователя по ID
def check_user_by_id(id) -> bool:
    res = db.users.find_one({'_id': ObjectId(id)})
    if res:
        return True
    return False


# проверка пользователя по номеру телефона
def check_user_by_phone(phone_number: str) -> bool:
    res = db.users.find_one({'phone_number': phone_number})
    if res:
        return True
    return False


# получение записей о всех пользователях
def get_users() -> MongoDBResult:
    res = db.users.find()
    if res:
        users = []
        for i in list(res):
            users.append(User(i))
        return MongoDBResult(True, users)
    else:
        return MongoDBResult(False, [])


# получение пользователя по ID
def get_user_by_id(id) -> MongoDBResult:
    user = db.users.find_one({'_id': ObjectId(id)})
    if user:
        # пользователь существует
        return MongoDBResult(True, User(user))
    else:
        # пользователя нет
        return MongoDBResult(False, None)


# получение пользователя по номеру телефона
def get_user_by_phone_number(phone_number: str) -> MongoDBResult:
    user = db.users.find_one({'phone_number': phone_number})
    if user:
        # пользователь существует
        return MongoDBResult(True, User(user))
    else:
        # пользователя нет
        return MongoDBResult(False, None)


# добавление пользователя
def add_user(phone_number: str, password: str):
    db.users.insert_one({
        "phone_number": phone_number,
        "password": password,
        "telegram_id": None,
        "first_name": None,
        "last_name": None,
        "role": "student",
        "reward_type": None
    })


# добавление пользователей
def add_users(users):
    db.users.insert_many(users)


# обновление данных пользователя по ID
def update(id, key, value):
    db.users.update_one({'_id': ObjectId(id)}, {"$set": {key: value}})


# удаление пользователя по ID
def delete_user(id):
    db.users.delete_one({
        '_id': ObjectId(id)
    })


# очистка Документа
def truncate():
    db.users.drop()
