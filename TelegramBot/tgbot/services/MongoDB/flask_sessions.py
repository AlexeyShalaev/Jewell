from TelegramBot.tgbot.models.flask_session import *
from . import db, MongoDBResult

"""
Это собственно-написанная ORM - для NoSql базы данных MongoDB, для взаимодействия с моделью FlaskSession
Документ: flask_sessions
"""


# получение записей о всех сессиях по ID пользователя
def get_flask_sessions_by_user_id(user_id) -> MongoDBResult:
    res = db.flask_sessions.find({'user_id': ObjectId(user_id)})
    if res:
        flask_sessions = []
        for i in list(res):
            flask_sessions.append(FlaskSession(i))
        return MongoDBResult(True, flask_sessions)
    else:
        return MongoDBResult(False, [])


# удаление сессии по ID
def delete_flask_session(id):
    try:
        db.flask_sessions.delete_one({
            '_id': id
        })
    except Exception as ex:
        print(ex)


# удаление сессий по user_id
def delete_flask_sessions_by_user_id(user_id):
    try:
        db.flask_sessions.delete_many({
            'user_id': ObjectId(user_id)
        })
    except Exception as ex:
        print(ex)
