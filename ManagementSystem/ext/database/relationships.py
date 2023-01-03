from ManagementSystem.ext.models.relationship import *
from . import db, MongoDBResult

"""
Это собственно-написанная ORM - для NoSql базы данных MongoDB, для взаимодействия с моделью Relationship
Документ: relationships
"""


# получение всех связей
def get_relationships() -> MongoDBResult:
    res = db.relationships.find()
    if res:
        relationships = []
        for i in list(res):
            relationships.append(Relationship(i))
        return MongoDBResult(True, relationships)
    else:
        return MongoDBResult(False, [])


# получение связей по отправителю
def get_relationships_by_sender(sender) -> MongoDBResult:
    res = db.relationships.find({'sender': ObjectId(sender)})
    if res:
        relationships = []
        for i in list(res):
            relationships.append(Relationship(i))
        return MongoDBResult(True, relationships)
    else:
        return MongoDBResult(False, [])


# получение связей по отправителю
def get_relationships_by_receiver(receiver) -> MongoDBResult:
    res = db.relationships.find({'receiver': ObjectId(receiver)})
    if res:
        relationships = []
        for i in list(res):
            relationships.append(Relationship(i))
        return MongoDBResult(True, relationships)
    else:
        return MongoDBResult(False, [])


# получение связей по отправителю
def get_relationships_by_status(status: RelationStatus) -> MongoDBResult:
    res = db.relationships.find({'status': status.value})
    if res:
        relationships = []
        for i in list(res):
            relationships.append(Relationship(i))
        return MongoDBResult(True, relationships)
    else:
        return MongoDBResult(False, [])


# получение связи по ID
def get_relationship_by_id(id) -> MongoDBResult:
    relationship = db.relationships.find_one({'_id': ObjectId(id)})
    if relationship:
        # пользователь существует
        return MongoDBResult(True, relationship(relationship))
    else:
        # пользователя нет
        return MongoDBResult(False, None)


# добавление связи
def add_relationship(sender, receiver, status=RelationStatus.SUBMITTED):
    db.relationships.insert_one({
        "status": status.value,
        "sender": ObjectId(sender),
        "receiver": ObjectId(receiver)
    })


# добавление связей
def add_relationships(relationships):
    db.relationships.insert_many(relationships)


# обновление данных связи по ID
def update_relationship(id, key, value):
    db.relationships.update_one({'_id': ObjectId(id)}, {"$set": {key: value}})


# удаление связи по ID
def delete_relationship(id):
    db.relationships.delete_one({
        '_id': ObjectId(id)
    })


# очистка Документа
def truncate():
    db.relationships.drop()
