import json
from dataclasses import dataclass
from datetime import datetime

from TelegramBot.tgbot.misc.crypt import create_token


@dataclass
class Notification:
    id: str
    region: str  # Область действия
    link: str  # ссылка на регион
    icon: str  # mdi icon (class)
    color: str  # background
    text: str
    date: datetime

    def __init__(self, data):
        self.id = data['id']
        self.region = data['region']
        self.link = data['link']
        self.icon = data['icon']
        self.color = data['color']
        self.text = data['text']
        self.date = data['date']

    @staticmethod
    def create_notification(region, link, icon, color, text, date):
        status, data = create_token(4)
        return Notification(
            {
                'id': data,
                'region': region,
                'link': link,
                'icon': icon,
                'color': color,
                'text': text,
                'date': date.strftime("%d.%m.%Y %H:%M:%S")
            })

    def to_json(self):
        return {"id": self.id,
                "region": self.region,
                "link": self.link,
                "icon": self.icon,
                "color": self.color,
                "text": self.text,
                "date": self.date
                }

    def to_string_json(self):
        return json.dumps({"id": self.id,
                           "region": self.region,
                           "link": self.link,
                           "icon": self.icon,
                           "color": self.color,
                           "text": self.text,
                           "date": self.date
                           })
