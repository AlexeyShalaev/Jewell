import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from bson import ObjectId
from pytz import timezone

tz = timezone('Europe/Moscow')


class VisitType(Enum):
    ENTER = 'enter'  # вход
    EXIT = 'exit'  # выход


@dataclass
class Visit:
    id: ObjectId  # ID курса
    user_id: ObjectId  # ID пользователя
    date: datetime  # дата
    visit_type: VisitType  # тип посещения
    courses: list  # предполагаемый список курсов

    def __init__(self, data):
        self.id = data['_id']
        self.user_id = data['user_id']
        self.visit_type = VisitType(data['visit_type'])
        self.courses = data['courses']
        self.date = data['date']  # datetime.strptime(data['date'], "%d.%m.%Y %H:%M:%S")

    def to_json(self):
        return json.dumps({"_id": str(self.id),
                           "user_id": str(self.user_id),
                           "date": self.date.strftime("%d.%m.%Y %H:%M:%S"),
                           "visit_type": self.visit_type.value,
                           "courses": self.courses
                           })


class UnprocessedVisit:
    id: ObjectId  # ID курса
    user_id: ObjectId  # ID пользователя
    date: datetime  # дата

    def __init__(self, data):
        self.id = data['_id']
        self.user_id = data['user_id']
        self.date = tz.localize(data['date'])  # datetime.strptime(data['date'], "%d.%m.%Y %H:%M:%S")
