from Assistant.models.userModel import *
from . import db, MongoDBResult

"""
Это собственно-написанная ORM - для NoSql базы данных MongoDB, для взаимодействия с моделью User
Документ: users
"""


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


# обновление уведомлений пользователя
def update_notifications(id, notifications):
    db.users.update_one({'_id': ObjectId(id)}, {"$set": {'notifications': [i.to_json() for i in notifications]}})
