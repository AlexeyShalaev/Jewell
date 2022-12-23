from . import db, MongoDBResult
from AdminPanel.ext.models.attendance import *
from datetime import datetime

"""
Это собственно-написанная ORM - для NoSql базы данных MongoDB, для взаимодействия с моделью Attendance
Документ: attendances
"""


# получение записей о всех посещаемостях
def get_attendances() -> MongoDBResult:
    res = db.attendances.find()
    if res:
        attendances = []
        for i in list(res):
            attendances.append(Attendance(i))
        return MongoDBResult(True, attendances)
    else:
        return MongoDBResult(False, [])


# получение посещаемости по ID
def get_attendance_by_id(id) -> MongoDBResult:
    attendance = db.attendances.find_one({'_id': ObjectId(id)})
    if attendance:
        return MongoDBResult(True, Attendance(attendance))
    else:
        return MongoDBResult(False, None)


# получение посещаемости по User ID
def get_attendance_by_user_id(user_id) -> MongoDBResult:
    attendance = db.attendances.find_one({'user_id': ObjectId(user_id)})
    if attendance:
        return MongoDBResult(True, Attendance(attendance))
    else:
        return MongoDBResult(False, None)


# добавление посещаемости
def add_attendance(user_id, count, date):
    db.attendances.insert_one({
        "user_id": ObjectId(user_id),
        "count": count,
        "date": date.strftime("%d.%m.%Y %H:%M:%S")
    })


# добавление посещаемостей
def add_attendances(attendances):
    db.attendances.insert_many(attendances)


# обновление данных посещаемости по ID
def update_attendance(id, key, value):
    db.attendances.update_one({'_id': ObjectId(id)}, {"$set": {key: value}})


# удаление посещаемости по ID
def delete_attendance(id):
    db.attendances.delete_one({
        '_id': ObjectId(id)
    })


# очистка Документа
def truncate():
    db.attendances.drop()
