from ManagementSystem.ext.models.order import *
from . import db, MongoDBResult

"""
Это собственно-написанная ORM - для NoSql базы данных MongoDB, для взаимодействия с моделью order
Документ: orders
"""


# получение записей о всех заказах
def get_orders() -> MongoDBResult:
    res = db.orders.find()
    if res:
        orders = []
        for i in list(res):
            orders.append(Order(i))
        return MongoDBResult(True, orders)
    else:
        return MongoDBResult(False, [])


# получение записей о всех заказах по клиенту
def get_orders_by_client(client) -> MongoDBResult:
    res = db.orders.find({'client': ObjectId(client)})
    if res:
        orders = []
        for i in list(res):
            orders.append(Order(i))
        return MongoDBResult(True, orders)
    else:
        return MongoDBResult(False, [])


# получение записей о всех заказах по товару
def get_orders_by_product(product) -> MongoDBResult:
    res = db.orders.find({'product': ObjectId(product)})
    if res:
        orders = []
        for i in list(res):
            orders.append(Order(i))
        return MongoDBResult(True, orders)
    else:
        return MongoDBResult(False, [])


# получение записей о всех заказах по статусу
def get_orders_by_status(status: OrderStatus) -> MongoDBResult:
    res = db.orders.find({'status': status.value})
    if res:
        orders = []
        for i in list(res):
            orders.append(Order(i))
        return MongoDBResult(True, orders)
    else:
        return MongoDBResult(False, [])


# получение заказа по ID
def get_order_by_id(id) -> MongoDBResult:
    order = db.orders.find_one({'_id': ObjectId(id)})
    if order:
        # пользователь существует
        return MongoDBResult(True, Order(order))
    else:
        # пользователя нет
        return MongoDBResult(False, None)


# добавление заказа
def add_order(product, client, address, country, city, zip_postal, comments, status=OrderStatus.PlACED):
    db.orders.insert_one({
        "product": ObjectId(product),
        "client": ObjectId(client),
        "address": address,
        "country": country,
        "city": city,
        "zip_postal": zip_postal,
        "comments": comments,
        "timestamp": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
        "status": status.value
    })


# добавление заказов
def add_orders(orders):
    db.orders.insert_many(orders)


# обновление данных заказа по ID
def update_order(id, key, value):
    db.orders.update_one({'_id': ObjectId(id)}, {"$set": {key: value}})


# удаление заказа по ID
def delete_order(id):
    db.orders.delete_one({
        '_id': ObjectId(id)
    })


# очистка Документа
def truncate():
    db.orders.drop()
