from ManagementSystem.ext.models.userModel import *
from . import db, MongoDBResult

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


# получение записей о всех пользователях по роли
def get_users_by_role(role: Role) -> MongoDBResult:
    res = db.users.find({'role': role.value})
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


# получение пользователя по access_token
def get_user_by_access_token(access_token: str) -> MongoDBResult:
    user = db.users.find_one({'access_token': access_token})
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
        "telegram_username": None,
        "telegram_auth": False,
        "first_name": None,
        "last_name": None,
        "sex": "null",
        "birthday": None,
        "role": Role.REGISTERED.value,
        "reward": Reward.NULL.value,
        "access_token": None,
        "profession": None,
        "university": None,
        "languages": None,
        "location": None,
        "tags": None,
        "notifications": [],
        "points": 0
    })


# добавление пользователей
def add_users(users):
    db.users.insert_many(users)


# обновление данных пользователя по ID
def update_user(id, key, value):
    db.users.update_one({'_id': ObjectId(id)}, {"$set": {key: value}})


# обновление уведомлений пользователя
def update_notifications(id, notifications):
    db.users.update_one({'_id': ObjectId(id)}, {"$set": {'notifications': [i.to_json() for i in notifications]}})


def update_registered_user(id, first_name, last_name, birthday):
    db.users.update_one({'_id': ObjectId(id)}, {"$set": {
        "first_name": first_name,
        "last_name": last_name,
        "birthday": birthday
    }})


def update_social_data(id, sex, location, profession, university, languages, tags):
    db.users.update_one({'_id': ObjectId(id)}, {"$set": {
        "sex": sex,
        "location": location,
        "profession": profession,
        "university": university,
        "languages": languages,
        "tags": tags,
    }})


def update_main_data(id, first_name, last_name, phone_number, birthday, reward):
    db.users.update_one({'_id': ObjectId(id)}, {"$set": {
        "first_name": first_name,
        "last_name": last_name,
        "phone_number": phone_number,
        "birthday": birthday,
        "reward": reward
    }})


def update_new_user(id, first_name, last_name, birthday, role):
    db.users.update_one({'_id': ObjectId(id)}, {"$set": {
        "first_name": first_name,
        "last_name": last_name,
        "birthday": birthday,
        "role": role
    }})


# удаление пользователя по ID
def delete_user(id):
    db.users.delete_one({
        '_id': ObjectId(id)
    })


# очистка Документа
def truncate():
    db.users.drop()
