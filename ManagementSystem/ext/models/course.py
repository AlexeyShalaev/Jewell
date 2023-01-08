import json
import re
from dataclasses import dataclass

from bson import ObjectId


@dataclass
class Time:
    hours: int
    minutes: int

    def to_json(self):
        return json.dumps({"hours": self.hours,
                           "minutes": self.minutes
                           })

    def to_string(self):
        return f'{self.hours}:{self.minutes}'

    @staticmethod
    def from_json(data):
        return Time(data['hours'], data['minutes'])

    @staticmethod
    def from_string(stroka):
        arr = re.split(r'\D', stroka)
        return Time(int(arr[0]), int(arr[1]))

    def __gt__(self, time):
        if self.hours == time.hours:
            return self.minutes > time.minutes
        return self.hours > time.hours

    def __lt__(self, time):
        if self.hours == time.hours:
            return self.minutes < time.minutes
        return self.hours < time.hours


@dataclass
class Course:
    id: ObjectId  # ID курса
    teachers: list  # список учителей
    name: str  # название
    timetable: dict  # расписание

    def __init__(self, data):
        self.id = data['_id']
        self.teachers = data['teachers']
        self.name = data['name']
        timetable = dict()
        for k, v in data['timetable'].items():
            js = json.loads(v)
            timetable[k] = Time.from_json(js)
        self.timetable = timetable

    def to_json(self):
        return json.dumps({"_id": str(self.id),
                           "teachers": self.teachers,
                           "name": self.name,
                           "timetable": self.timetable,
                           })
