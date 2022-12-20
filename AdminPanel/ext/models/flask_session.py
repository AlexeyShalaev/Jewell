from dataclasses import dataclass
from bson import ObjectId
import json


@dataclass
class FlaskSession:
    id: str
    fresh: bool
    user_id: ObjectId
    ip: str

    def __init__(self, data):
        self.id = data['_id']
        self.fresh = data['fresh']
        self.user_id = data['user_id']
        self.ip = data['ip']

    def to_json(self):
        return json.dumps({"_id": str(self.id),
                           "fresh": self.fresh,
                           "user_id": self.user_id,
                           "ip": self.ip
                           })
