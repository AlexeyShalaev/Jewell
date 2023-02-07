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


# обновление данных пользователя по ID
def update_auth_token(id, token):
    db.users.update_one({'_id': ObjectId(id)}, {"$set": {"access_token": token}})
