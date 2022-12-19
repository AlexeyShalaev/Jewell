from dataclasses import dataclass
from bson import ObjectId
import json


@dataclass
class RecoverPW:
    id: ObjectId  # ID запроса на восстановление
    phone_number: str  # номер телефона
    user_id: ObjectId  # ID пользователя
    telegram_id: int  # telegram chat id

    def __init__(self, data):
        self.id = data['_id']
        self.phone_number = data['phone_number']
        self.user_id = data['user_id']
        self.telegram_id = data['telegram_id']

    def to_json(self):
        # TODO: проверить , что JSON-serializer работает корректно
        return json.dumps({"_id": str(self.id),
                           "phone_number": self.phone_number,
                           "user_id": self.user_id,
                           "telegram_id": self.telegram_id,
                           })
