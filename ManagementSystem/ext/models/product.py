import json
from dataclasses import dataclass

from bson import ObjectId


@dataclass
class Product:
    id: ObjectId  # ID заказа
    name: str  # имя товара
    info: str  # небольшая информация (описание)
    price: str  # цена

    def __init__(self, data):
        self.id = data['_id']
        self.name = data['name']
        self.info = data['info']
        self.price = data['price']

    def to_json(self):
        return json.dumps({"_id": str(self.id),
                           "name": self.name,
                           "info": self.info,
                           "price": self.price
                           })
