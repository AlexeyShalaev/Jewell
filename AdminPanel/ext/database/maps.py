from . import db, MongoDBResult
from AdminPanel.ext.models.map import *

"""
Это собственно-написанная ORM - для NoSql базы данных MongoDB, для взаимодействия с моделью Map
Документ: maps
"""


# получение записей о всех картах
def get_maps() -> MongoDBResult:
    res = db.maps.find()
    if res:
        maps = []
        for i in list(res):
            maps.append(Map(i))
        return MongoDBResult(True, maps)
    else:
        return MongoDBResult(False, [])


# получение карты по ID
def get_map_by_id(id) -> MongoDBResult:
    map = db.maps.find_one({'_id': ObjectId(id)})
    if map:
        return MongoDBResult(True, Map(map))
    else:
        return MongoDBResult(False, None)


# получение карты по названию
def get_map_by_name(name: str) -> MongoDBResult:
    map = db.maps.find_one({'name': name})
    if map:
        return MongoDBResult(True, Map(map))
    else:
        return MongoDBResult(False, None)


# добавление карты
def add_map(name, countries):
    db.maps.insert_one({
        "name": name,
        "countries": countries
    })


# добавление оферов
def add_maps(maps):
    db.maps.insert_many(maps)


# обновление данных карты по ID
def update_map(id, key, value):
    db.maps.update_one({'_id': ObjectId(id)}, {"$set": {key: value}})


# удаление карты по ID
def delete_map(id):
    db.maps.delete_one({
        '_id': ObjectId(id)
    })


# очистка Документа
def truncate():
    db.maps.drop()
