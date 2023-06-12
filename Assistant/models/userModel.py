from enum import Enum

from bson import ObjectId

from Assistant.models.notification import Notification


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


class User:
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
    notifications: list  # уведомления
    points: int

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
        self.notifications = [Notification(i) for i in data['notifications']]
        self.points = data['points']