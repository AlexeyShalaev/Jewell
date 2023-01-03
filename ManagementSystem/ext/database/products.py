from ManagementSystem.ext.models.product import *
from . import db, MongoDBResult

"""
Это собственно-написанная ORM - для NoSql базы данных MongoDB, для взаимодействия с моделью product
Документ: products
"""


# проверка пользователя по ID
def check_product_by_id(id) -> bool:
    res = db.products.find_one({'_id': ObjectId(id)})
    if res:
        return True
    return False


# получение записей о всех товарах
def get_products() -> MongoDBResult:
    res = db.products.find()
    if res:
        products = []
        for i in list(res):
            products.append(Product(i))
        return MongoDBResult(True, products)
    else:
        return MongoDBResult(False, [])


# получение товара по ID
def get_product_by_id(id) -> MongoDBResult:
    product = db.products.find_one({'_id': ObjectId(id)})
    if product:
        # пользователь существует
        return MongoDBResult(True, Product(product))
    else:
        # пользователя нет
        return MongoDBResult(False, None)


# добавление товара
def add_product(name, info, price):
    db.products.insert_one({
        "name": name,
        "info": info,
        "price": price
    })


# добавление товаров
def add_products(products):
    db.products.insert_many(products)


# обновление данных товара по ID
def update_product(id, key, value):
    db.products.update_one({'_id': ObjectId(id)}, {"$set": {key: value}})


# удаление товара по ID
def delete_product(id):
    db.products.delete_one({
        '_id': ObjectId(id)
    })


# очистка Документа
def truncate():
    db.products.drop()
