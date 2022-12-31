from . import db, MongoDBResult
from ManagementSystem.ext.models.course import *

"""
Это собственно-написанная ORM - для NoSql базы данных MongoDB, для взаимодействия с моделью Course
Документ: courses
"""


# получение записей о всех курсах
def get_courses() -> MongoDBResult:
    res = db.courses.find()
    if res:
        courses = []
        for i in list(res):
            courses.append(Course(i))
        return MongoDBResult(True, courses)
    else:
        return MongoDBResult(False, [])


# получение курса по ID
def get_course_by_id(id) -> MongoDBResult:
    course = db.courses.find_one({'_id': ObjectId(id)})
    if course:
        return MongoDBResult(True, Course(course))
    else:
        return MongoDBResult(False, None)


# добавление курса
def add_course(teachers, name, timetable):
    db.courses.insert_one({
        "teachers": teachers,
        "name": name,
        "timetable": timetable
    })


# добавление курсов
def add_courses(courses):
    db.courses.insert_many(courses)


# обновление данных курса по ID
def update_course(id, key, value):
    db.courses.update_one({'_id': ObjectId(id)}, {"$set": {key: value}})


# удаление курса по ID
def delete_course(id):
    db.courses.delete_one({
        '_id': ObjectId(id)
    })


# очистка Документа
def truncate():
    db.courses.drop()


# no mongo queries

# поиск по названию
def get_courses_by_name(name: str) -> MongoDBResult:
    resp = get_courses()
    if resp.success:
        filtered_courses = []
        courses = resp.data
        for course in courses:
            if name in course.name:
                filtered_courses.append(course)
        return MongoDBResult(True, filtered_courses)
    else:
        return MongoDBResult(False, None)


# поиск учителю
def get_courses_by_teacher(teacher) -> MongoDBResult:
    resp = get_courses()
    if resp.success:
        filtered_courses = []
        courses = resp.data
        for course in courses:
            if teacher in course.teachers:
                filtered_courses.append(course)
        return MongoDBResult(True, filtered_courses)
    else:
        return MongoDBResult(False, None)


# поиск курсов по дню недели
def get_courses_by_day(day: str) -> MongoDBResult:
    resp = get_courses()
    if resp.success:
        filtered_courses = []
        courses = resp.data
        for course in courses:
            if day in course.timetable.keys():
                filtered_courses.append(course)
        return MongoDBResult(True, filtered_courses)
    else:
        return MongoDBResult(False, None)


# поиск курсов по времени HH:MM
def get_courses_by_time(time: str) -> MongoDBResult:
    resp = get_courses()
    if resp.success:
        filtered_courses = []
        courses = resp.data
        for course in courses:
            for k, v in course.timetable.items():
                if time == v:
                    filtered_courses.append(course)
                    break
        return MongoDBResult(True, filtered_courses)
    else:
        return MongoDBResult(False, None)
