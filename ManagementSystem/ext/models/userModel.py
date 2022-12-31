import json
from enum import Enum
from bson import ObjectId
from flask import url_for
from flask_login import UserMixin


class Reward(Enum):
    TRIP = 'trip'  # поездка
    GRANT = 'grant'  # стипендия
    NULL = 'null'  # ничего


class Role(Enum):
    REGISTERED = 'registered'  # зарегистрированный пользователь, ждущий одобрения принятия
    STUDENT = 'student'  # студент
    TEACHER = 'teacher'  # учитель
    ADMIN = 'admin'  # админ
    NULL = 'null'  # ничего


class Sex(Enum):
    MALE = 'male'  # М
    FEMALE = 'female'  # Ж
    NULL = 'null'  # ничего


class User(UserMixin):
    id: ObjectId
    phone_number: str  # 89854839731
    password: str  # qwerty1234
    telegram_id: int  # 703757403 - telegram chat id
    telegram_username: str  # Alexey1537 - telegram user name
    telegram_auth: bool  # false
    first_name: str  # alex
    last_name: str  # shalaev
    sex: Sex  # пол
    birthday: str  # 27.05.2004
    role: Role  # student/teacher/admin
    reward: Reward  # trip/grant/none
    access_token: str  # поле для хранения временного токена, который можно использовать для подтверждений чего-либо
    profession: str  # профессия
    university: str  # учебное заведение
    languages: list  # языки
    location: str  # местонахождение
    tags: list  # теги

    def __init__(self, data):
        self.id = data['_id']
        self.phone_number = data['phone_number']
        self.password = data['password']
        self.telegram_id = data['telegram_id']
        self.telegram_username = data['telegram_username']
        self.telegram_auth = data['telegram_auth']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.sex = Sex(data['sex'])
        self.birthday = data['birthday']
        self.role = Role(data['role'])
        self.reward = Reward(data['reward'])
        self.access_token = data['access_token']
        self.profession = data['profession']
        self.university = data['university']
        self.languages = data['languages']
        self.location = data['location']
        self.tags = data['tags']

    def to_json(self):
        return json.dumps({"_id": str(self.id),
                           "phone_number": self.phone_number,
                           "password": self.password,
                           "telegram_id": self.telegram_id,
                           "telegram_username": self.telegram_username,
                           "telegram_auth": self.telegram_auth,
                           "first_name": self.first_name,
                           "last_name": self.last_name,
                           "sex": self.sex.value,
                           "birthday": self.birthday,
                           "role": self.role.value,
                           "reward": self.reward.value,
                           "access_token": self.access_token,
                           "profession": self.profession,
                           "university": self.university,
                           "languages": self.languages,
                           "location": self.location,
                           "tags": self.tags
                           })

    def to_document(self):
        return {
            'id': str(self.id),
            'data': f'{self.telegram_username} {self.first_name} {self.last_name} {self.sex.value} {self.birthday}'
                    f' {self.reward.value} {self.profession} {self.university} {self.location}'
                    f' {" ".join(self.languages)} {" ".join(self.tags)}'}

    def to_net(self):
        return {"id": str(self.id), "name": f'<a href=\"{self.get_page()}\" target="_blank">{self.first_name} {self.last_name}</a>',
                "telegram": f'<a href=\"https://t.me/{self.telegram_username}\" target="_blank">@{self.telegram_username}</a>' if self.telegram_username else "-",
                }

    def get_page(self):
        if self.role == Role.STUDENT:
            return url_for('networking.profile', user_id=str(self.id))
        return ""
