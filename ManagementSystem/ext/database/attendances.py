from ManagementSystem.ext.models.attendance import *
from . import db, MongoDBResult

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


def get_filtered_attendances(start: int, end: int, chosen_month: int):
    # Создаем фильтр
    filter_condition = {
        "$or": [
            {"$and": [{"date.year": start}, {"date.month": {"$gte": 9}}]},
            {"$and": [{"date.year": end}, {"date.month": {"$lt": 9}}]}
        ],
        "date.month": chosen_month
    }

    # Выполняем запрос с фильтром
    res = db.attendances.find(filter_condition).sort("date", 1)

    # Обрабатываем результат
    if res:
        return [Attendance(i) for i in res]
    else:
        return []


# получение посещаемости по ID
def get_attendance_by_id(id) -> MongoDBResult:
    attendance = db.attendances.find_one({'_id': ObjectId(id)})
    if attendance:
        return MongoDBResult(True, Attendance(attendance))
    else:
        return MongoDBResult(False, None)


# получение посещаемостей по User ID
def get_attendances_by_user_id(user_id) -> MongoDBResult:
    res = db.attendances.find({'user_id': ObjectId(user_id)})
    if res:
        attendances = []
        for i in list(res):
            attendances.append(Attendance(i))
        return MongoDBResult(True, attendances)
    else:
        return MongoDBResult(False, [])


# добавление посещаемости
def add_attendance(user_id, count, date):
    db.attendances.insert_one({
        "user_id": ObjectId(user_id),
        "count": int(count),
        "date": date
    })


# добавление посещаемостей
def add_attendances(attendances):
    db.attendances.insert_many(attendances)


# обновление данных посещаемости по ID
def update_attendance(id, date, count):
    db.attendances.update_one({'_id': ObjectId(id)}, {"$set": {
        "date": date,
        "count": int(count),
    }})


# удаление посещаемости по ID
def delete_attendance(id):
    db.attendances.delete_one({
        '_id': ObjectId(id)
    })


# очистка Документа
def truncate():
    db.attendances.drop()


# Markers

def add_attendance_marker(name, start, finish):
    db.attendance_markers.insert_one({
        "name": name,
        "start": start,
        "finish": finish,
        "students": []
    })


def update_attendance_marker(id, name, start, finish):
    db.attendance_markers.update_one({'_id': ObjectId(id)}, {"$set": {
        "name": name,
        "start": start,
        "finish": finish
    }})


def join_attendance_marker(id, student_id):
    db.attendance_markers.update_one({'_id': ObjectId(id)}, {'$addToSet': {'students': student_id}})


def get_attendance_markers() -> MongoDBResult:
    res = db.attendance_markers.find()
    if res:
        attendance_markers = []
        for i in list(res):
            attendance_markers.append(AttendanceMarker(i))
        return MongoDBResult(True, attendance_markers)
    else:
        return MongoDBResult(False, [])


def get_attendance_marker_by_id(id) -> MongoDBResult:
    r = db.attendance_markers.find_one({'_id': ObjectId(id)})
    if r:
        return MongoDBResult(True, AttendanceMarker(r))
    else:
        return MongoDBResult(False, None)


def delete_attendance_marker(id):
    db.attendance_markers.delete_one({
        '_id': ObjectId(id)
    })


def delete_attendances_by_user_id(user_id):
    db.attendances.delete_many({
        'user_id': ObjectId(user_id)
    })
