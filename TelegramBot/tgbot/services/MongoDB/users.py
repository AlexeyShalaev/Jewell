from TelegramBot.tgbot.models.userModel import *
from . import db, MongoDBResult

"""
Это собственно-написанная ORM - для NoSql базы данных MongoDB, для взаимодействия с моделью User
Документ: users
"""


# проверка пользователя по telegram ID
def check_user_by_telegram_id(telegram_id) -> bool:
    res = db.users.find_one({'telegram_id': telegram_id})
    if res:
        return True
    return False


# получение пользователя по telegram ID
def get_user_by_telegram_id(telegram_id) -> MongoDBResult:
    user = db.users.find_one({'telegram_id': telegram_id})
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


# обновление данных пользователя по ID
def update_auth_token(id, token):
    db.users.update_one({'_id': ObjectId(id)}, {"$set": {"access_token": token}})


# обновление данных пользователя по ID
def update_telegram_data(id, tg_id, tg_name):
    db.users.update_one({'_id': ObjectId(id)},
                        {"$set": {"telegram_id": tg_id, "telegram_username": tg_name, "access_token": ''}})


# обновление уведомлений пользователя
def update_notifications(id, notifications):
    db.users.update_one({'_id': ObjectId(id)}, {"$set": {'notifications': [i.to_json() for i in notifications]}})
