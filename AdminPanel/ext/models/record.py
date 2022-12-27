from dataclasses import dataclass
from bson import ObjectId
from datetime import datetime
import json
from AdminPanel.ext.database.users import get_user_by_id


@dataclass
class Record:
    id: ObjectId  # ID записи
    author: ObjectId  # ID автора
    text: str  # текст записи
    time: datetime  # время публикации

    def __init__(self, data):
        self.id = data['_id']
        self.author = data['author']
        self.text = data['text']
        self.time = data['time']

    def to_json(self):
        return json.dumps({"_id": str(self.id),
                           "author": str(self.author),
                           "text": self.text,
                           "time": self.time.strftime("%d.%m.%Y %H:%M"),
                           })

    def to_document(self):
        resp = get_user_by_id(self.author)
        if resp.success:
            return {'id': str(self.id),
                    'data': f'{self.text} {self.time} {resp.data.first_name} {resp.data.last_name}'}
        else:
            return {'id': str(self.id),
                    'data': f'{self.text} {self.time}'}

    def get_time_date(self):
        return self.time.strftime("%d.%m.%Y")

    def get_time_time(self):
        return self.time.strftime("%H:%M")
