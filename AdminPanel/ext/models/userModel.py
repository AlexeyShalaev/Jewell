from enum import Enum
from bson import ObjectId
import json
from flask_login import UserMixin


class Reward(Enum):
    TRIP = 'trip'  # поездка
    GRANT = 'grant'  # стипендия
    NULL = 'null'  # ничего


class Role(Enum):
    STUDENT = 'student'  # студент
    TEACHER = 'teacher'  # учитель
    ADMIN = 'admin'  # админ


class User(UserMixin):
    id: ObjectId
    phone_number: str  # 79854839731
    password: str  # qwerty1234
    telegram_id: int  # 703757403 - telegram chat id
    first_name: str  # alex
    last_name: str  # shalaev
    role: Role  # student/teacher/admin
    reward_type: Reward  # trip/grant/none

    def __init__(self, data):
        self.id = data['_id']
        self.phone_number = data['phone_number']
        self.password = data['password']
        self.telegram_id = data['telegram_id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.role = Role(data['role'])
        self.reward_type = Reward(data['reward_type'])

    def to_json(self):
        # TODO: проверить , что JSON-serializer работает корректно
        return json.dumps({"_id": int(str(self.id)),
                           "phone_number": self.phone_number,
                           "password": self.password,
                           "telegram_id": self.telegram_id,
                           "first_name": self.first_name,
                           "last_name": self.last_name,
                           "role": self.role,
                           "reward_type": self.reward_type,
                           })

    """
    {
      "_id": {
        "$oid": "********************"
      },
    "phone_number": "89854839731",
    "password": "1",
    "telegram_id": 703757403,
    "first_name": "alex",
    "last_name": "shalaev",
    "role": "student",
    "reward_type": "trip"
    }
    """


"""
TODO



class Visit(Document):
    date: datetime
    count: int
    student_id: PydanticObjectId

    class Settings:
        name = "visits"  # database document name


class Event(Document):
    name: str
    place: str
    comment: str
    errors: str
    poster: str
    sent_count: int
    sent_to_count: int
    timestamp: datetime
    published: bool
    deleted: bool

    class Settings:
        name = "events"  # database document name


class EventReminder(Document):
    chat_id: str
    event_id: PydanticObjectId

    class Settings:
        name = "eventreminder"  # database document name


class Option(Document):
    option: str
    vote_id: PydanticObjectId
    count_of_votes: int

    class Settings:
        name = "options"  # database document name


class UserVote(Document):
    user_id: PydanticObjectId
    vote_id: PydanticObjectId

    class Settings:
        name = "usersvotes"  # database document name


class Vote(Document):
    start: datetime
    end: datetime
    name: str
    question: str
    user: str
    closed: int
    published: int

    class Settings:
        name = "votes"  # database document name
"""
