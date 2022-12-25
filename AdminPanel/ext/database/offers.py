from . import db, MongoDBResult
from AdminPanel.ext.models.offer import *

"""
Это собственно-написанная ORM - для NoSql базы данных MongoDB, для взаимодействия с моделью Offer
Документ: offers
"""


# проверка офера по ID
def check_offer_by_id(id) -> bool:
    res = db.offers.find_one({'_id': ObjectId(id)})
    if res:
        return True
    return False


# проверка офера по id автора
def check_offer_by_author(author) -> bool:
    res = db.offers.find_one({'author': ObjectId(author)})
    if res:
        return True
    return False


# получение записей о всех оферах
def get_offers() -> MongoDBResult:
    res = db.offers.find()
    if res:
        offers = []
        for i in list(res):
            offers.append(Offer(i))
        return MongoDBResult(True, offers)
    else:
        return MongoDBResult(False, [])


# получение записей о всех оферах по автору
def get_offers_by_author(author) -> MongoDBResult:
    res = db.offers.find({'author': ObjectId(author)})
    if res:
        offers = []
        for i in list(res):
            offers.append(Offer(i))
        return MongoDBResult(True, offers)
    else:
        return MongoDBResult(False, [])


# получение офера по ID
def get_offer_by_id(id) -> MongoDBResult:
    offer = db.offers.find_one({'_id': ObjectId(id)})
    if offer:
        # пользователь существует
        return MongoDBResult(True, Offer(offer))
    else:
        # пользователя нет
        return MongoDBResult(False, None)


# добавление офера
def add_offer(author, name, description, start, finish, reward):
    db.offers.insert_one({
        "author": ObjectId(author),
        "name": name,
        "description": description,
        "start": start,
        "finish": finish,
        "reward": reward
    })


# добавление оферов
def add_offers(offers):
    db.offers.insert_many(offers)


# обновление данных офера по ID
def update_offer(id, key, value):
    db.offers.update_one({'_id': ObjectId(id)}, {"$set": {key: value}})


# удаление офера по ID
def delete_offer(id):
    db.offers.delete_one({
        '_id': ObjectId(id)
    })


# очистка Документа
def truncate():
    db.offers.drop()
