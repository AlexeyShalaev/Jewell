from dataclasses import dataclass
from bson import ObjectId
from datetime import datetime
import json


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
        return f'{self.text} {self.time}'

    def get_time_date(self):
        return self.time.strftime("%d.%m.%Y")

    def get_time_time(self):
        return self.time.strftime("%H:%M")
