from Assistant.models.record import *
from . import db, MongoDBResult

"""
Это собственно-написанная ORM - для NoSql базы данных MongoDB, для взаимодействия с моделью Record
Документ: records
"""


# получение всех записей
def get_records() -> MongoDBResult:
    res = db.records.find()
    if res:
        records = []
        for i in list(res):
            records.append(Record(i))
        return MongoDBResult(True, records)
    else:
        return MongoDBResult(False, [])
