import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from bson import ObjectId


class FormStatus(Enum):
    CLOSED = 'closed'  # закрыт
    OPENED = 'opened'  # открыт
    NULL = 'null'  # ничего


@dataclass
class Form:
    id: ObjectId  # ID формы
    timestamp: datetime
    status: FormStatus
    name: str  # название формы
    description: str  # описание
    content: str  # контент

    def __init__(self, data):
        self.id = data['_id']
        self.timestamp = datetime.strptime(data['timestamp'], "%d.%m.%Y %H:%M:%S")
        self.status = FormStatus(data['status'])
        self.name = data['name']
        self.description = data['description']
        self.content = data['content']

    def to_json(self):
        return json.dumps({"_id": str(self.id),
                           "name": self.name,
                           "description": self.description,
                           "content": self.content,
                           "timestamp": self.timestamp.strftime("%d.%m.%Y %H:%M"),
                           "status": self.status.value,
                           })

    def get_timestamp(self):
        return self.timestamp.strftime("%d.%m.%Y %H:%M:%S")


@dataclass
class FormAnswer:
    id: ObjectId  # ID ответа на форму
    form: ObjectId
    author: ObjectId
    timestamp: datetime
    content: str

    def __init__(self, data):
        self.id = data['_id']
        self.form = data['form']
        self.author = data['author']
        self.timestamp = datetime.strptime(data['timestamp'], "%d.%m.%Y %H:%M:%S")
        self.content = data['content']

    def to_json(self):
        return json.dumps({"_id": str(self.id),
                           "form": str(self.form),
                           "author": str(self.author),
                           "content": self.content,
                           "timestamp": self.timestamp.strftime("%d.%m.%Y %H:%M"),
                           })

    def get_timestamp(self):
        return self.timestamp.strftime("%d.%m.%Y %H:%M:%S")
