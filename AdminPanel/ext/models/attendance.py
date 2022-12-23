from dataclasses import dataclass
from datetime import datetime
from bson import ObjectId
import json


@dataclass
class Attendance:
    id: ObjectId  # ID курса
    user_id: ObjectId  # ID пользователя
    count: int  # количество
    date: datetime  # дата

    def __init__(self, data):
        self.id = data['_id']
        self.user_id = data['user_id']
        self.count = data['count']
        self.date = datetime.strptime(data['date'], "%d.%m.%Y %H:%M:%S")

    def to_json(self):
        return json.dumps({"_id": str(self.id),
                           "user_id": str(self.user_id),
                           "count": self.count,
                           "date": self.date.strftime("%d.%m.%Y %H:%M:%S"),
                           })
