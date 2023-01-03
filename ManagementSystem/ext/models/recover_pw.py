import json
from dataclasses import dataclass

from bson import ObjectId


@dataclass
class RecoverPW:
    id: ObjectId  # ID запроса на восстановление
    phone_number: str  # номер телефона
    user_id: ObjectId  # ID пользователя

    def __init__(self, data):
        self.id = data['_id']
        self.phone_number = data['phone_number']
        self.user_id = data['user_id']

    def to_json(self):
        return json.dumps({"_id": str(self.id),
                           "phone_number": self.phone_number,
                           "user_id": self.user_id
                           })
