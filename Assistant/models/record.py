import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from bson import ObjectId


class RecordType(Enum):
    NEWS = 'news'  # новости (только учителя и админы)
    POST = 'post'  # пост (все)
    NULL = 'null'  # ничего


@dataclass
class Record:
    id: ObjectId  # ID записи
    author: ObjectId  # ID автора
    type: RecordType  # тип записи
    text: str  # текст записи
    time: datetime  # время публикации
    lifetime: int  # время действия <=0 -> бессрочно. >0 число дней

    def __init__(self, data):
        self.id = data['_id']
        self.author = data['author']
        self.type = RecordType(data['type'])
        self.text = data['text']
        self.time = data['time']
        self.lifetime = data['lifetime']

    def to_json(self):
        return json.dumps({"_id": str(self.id),
                           "author": str(self.author),
                           "type": self.type.value,
                           "text": self.text,
                           "time": self.time.strftime("%d.%m.%Y %H:%M"),
                           "lifetime": self.lifetime,
                           })
