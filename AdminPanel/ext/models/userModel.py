from enum import Enum

from bunnet import Document, PydanticObjectId
from flask_login import UserMixin


class Reward(Enum):
    TRIP = 'trip'  # поездка
    GRANT = 'grant'  # стипендия
    NULL = 'null'  # ничего


class Role(Enum):
    STUDENT = 'student'  # студент
    TEACHER = 'teacher'  # учитель
    ADMIN = 'admin'  # админ


class User(Document, UserMixin):
    id: PydanticObjectId
    phone_number: str  # 79854839731
    password: str  # qwerty1234
    user_id: int  # 703757403 - telegram chat id
    first_name: str  # alex
    last_name: str  # shalaev
    role: Role  # student/teacher/admin
    reward_type: Reward  # trip/grant/none

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print('constructor')

    """
    {
      "_id": {
        "$oid": "********************"
      },
    "phone_number": "89854839731",
    "password": "1",
    "user_id": 703757403,
    "first_name": "alex",
    "last_name": "shalaev",
    "role": "student",
    "reward_type": "trip"
    }
    """

    class Settings:
        name = "users"  # database document name


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
