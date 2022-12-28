from . import db, MongoDBResult
from AdminPanel.ext.models.flask_session import *

"""
Это собственно-написанная ORM - для NoSql базы данных MongoDB, для взаимодействия с моделью FlaskSession
Документ: flask_sessions
"""


# получение записей о всех сессиях
def get_flask_sessions() -> MongoDBResult:
    res = db.flask_sessions.find()
    if res:
        flask_sessions = []
        for i in list(res):
            flask_sessions.append(FlaskSession(i))
        return MongoDBResult(True, flask_sessions)
    else:
        return MongoDBResult(False, [])


# получение записей о всех сессиях по роли
def get_flask_sessions_by_user_id(user_id) -> MongoDBResult:
    res = db.flask_sessions.find({'user_id': ObjectId(user_id)})
    if res:
        flask_sessions = []
        for i in list(res):
            flask_sessions.append(FlaskSession(i))
        return MongoDBResult(True, flask_sessions)
    else:
        return MongoDBResult(False, [])


# получение сессии по ID
def get_flask_session_by_id(id) -> MongoDBResult:
    flask_session = db.flask_sessions.find_one({'_id': id})
    if flask_session:
        # сессия существует
        return MongoDBResult(True, FlaskSession(flask_session))
    else:
        # сессии нет
        return MongoDBResult(False, None)


# добавление сессии
def add_flask_session(id, user_id, user_agent, fresh, ip):
    try:
        if get_flask_session_by_id(id).success:
            delete_flask_session(id)
        db.flask_sessions.insert_one({
            '_id': id,
            "user_id": ObjectId(user_id),
            "user_agent": str(user_agent),
            "fresh": fresh,
            "ip": ip
        })
    except Exception as ex:
        print(ex)


# добавление сессий
def add_flask_sessions(flask_sessions):
    db.flask_sessions.insert_many(flask_sessions)


# удаление сессии по ID
def delete_flask_session(id):
    try:
        db.flask_sessions.delete_one({
            '_id': id
        })
    except Exception as ex:
        print(ex)


# удаление сессий по user_id
def delete_flask_sessions(user_id):
    try:
        db.flask_sessions.delete_many({
            'user_id': ObjectId(user_id)
        })
    except Exception as ex:
        print(ex)


# очистка Документа
def truncate():
    db.flask_sessions.drop()
