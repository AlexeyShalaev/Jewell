import json
from dataclasses import dataclass
from datetime import datetime

from bson import ObjectId


@dataclass
class Offer:
    id: ObjectId  # ID офера
    author: ObjectId  # ID автора
    name: str  # название
    description: str  # описание
    start: datetime
    finish: datetime
    reward: str

    def __init__(self, data):
        self.id = data['_id']
        self.author = data['author']
        self.name = data['name']
        self.description = data['description']
        self.start = data['start']
        self.finish = data['finish']
        self.reward = data['reward']

    def to_json(self):
        return json.dumps({"_id": str(self.id),
                           "author": str(self.author),
                           "name": self.name,
                           "description": self.description,
                           "start": self.start.strftime("%d.%m.%Y %H:%M"),
                           "finish": self.finish.strftime("%d.%m.%Y %H:%M"),
                           "reward": self.reward
                           })

    def get_start_date(self):
        return self.start.strftime("%d.%m.%Y")

    def get_start_time(self):
        return self.start.strftime("%H:%M")

    def get_finish_date(self):
        return self.finish.strftime("%d.%m.%Y")

    def get_finish_time(self):
        return self.finish.strftime("%H:%M")
