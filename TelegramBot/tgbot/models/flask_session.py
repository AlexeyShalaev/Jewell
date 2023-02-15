import json
from dataclasses import dataclass

from bson import ObjectId


@dataclass
class FlaskSession:
    id: str
    fresh: bool
    user_id: ObjectId
    user_agent: str
    ip: dict

    def __init__(self, data):
        self.id = data['_id']
        self.fresh = data['fresh']
        self.user_id = data['user_id']
        self.user_agent = data['user_agent']
        self.ip = data['ip']

    def to_json(self):
        return json.dumps({"_id": str(self.id),
                           "fresh": self.fresh,
                           "user_id": self.user_id,
                           "user_agent": self.user_agent,
                           "ip": self.ip
                           })
