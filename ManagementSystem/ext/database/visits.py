from ManagementSystem.ext.models.visit import *
from . import db, MongoDBResult

"""
Это собственно-написанная ORM - для NoSql базы данных MongoDB, для взаимодействия с моделью Visit
Документ: visits
"""


# получение записей о всех посещаемостях
def get_visits() -> MongoDBResult:
    res = db.visits.find()
    if res:
        visits = []
        for i in list(res):
            visits.append(Visit(i))
        return MongoDBResult(True, visits)
    else:
        return MongoDBResult(False, [])


# получение посещаемостей по User ID
def get_visits_by_user_id(user_id) -> MongoDBResult:
    res = db.visits.find({'user_id': ObjectId(user_id)})
    if res:
        visits = []
        for i in list(res):
            visits.append(Visit(i))
        return MongoDBResult(True, visits)
    else:
        return MongoDBResult(False, [])


# добавление посещаемости
def add_visit(user_id, date, visit_type, courses):
    db.visits.insert_one({
        "user_id": ObjectId(user_id),
        "date": date,
        "visit_type": visit_type.value,
        "courses": courses
    })


# добавление посещаемостей
def add_visits(visits):
    db.visits.insert_many(visits)


# очистка Документа
def truncate():
    db.visits.drop()


def add_unprocessed_visit(user_id, date):
    db.unprocessed_visits.insert_one({
        "user_id": ObjectId(user_id),
        "date": date
    })


def delete_visit_by_id(id):
    db.visits.delete_one({
        '_id': ObjectId(id)
    })


def delete_visits_by_user_id(user_id):
    db.visits.delete_many({
        'user_id': ObjectId(user_id)
    })
