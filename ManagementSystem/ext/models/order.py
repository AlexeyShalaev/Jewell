import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from bson import ObjectId


class OrderStatus(Enum):
    PlACED = 'placed'  # Размещенный заказ
    PACKED = 'packed'  # упакован
    SHIPPED = 'shipped'  # отправлен
    DELIVERED = 'delivered'  # доставлен
    NULL = 'null'  # ничего


@dataclass
class Order:
    id: ObjectId  # ID заказа
    product: ObjectId  # ID товара
    client: ObjectId  # ID клиента
    address: str
    country: str
    city: str
    zip_postal: str
    comments: str
    timestamp: datetime
    status: OrderStatus

    def __init__(self, data):
        self.id = data['_id']
        self.product = data['product']
        self.client = data['client']
        self.address = data['address']
        self.country = data['country']
        self.city = data['city']
        self.zip_postal = data['zip_postal']
        self.comments = data['comments']
        self.timestamp = datetime.strptime(data['timestamp'], "%d.%m.%Y %H:%M:%S")
        self.status = OrderStatus(data['status'])

    def to_json(self):
        return json.dumps({"_id": str(self.id),
                           "product": str(self.product),
                           "client": str(self.client),
                           "address": self.address,
                           "country": self.country,
                           "city": self.city,
                           "zip_postal": self.zip_postal,
                           "comments": self.comments,
                           "timestamp": self.timestamp.strftime("%d.%m.%Y %H:%M"),
                           "status": self.status.value,
                           })

    def get_timestamp(self):
        return self.timestamp.strftime("%d.%m.%Y %H:%M:%S")
