import json
from dataclasses import dataclass
from enum import Enum

from bson import ObjectId


class RelationStatus(Enum):
    ACCEPTED = 'accepted'  # принята
    SUBMITTED = 'submitted'  # отправлена
    NULL = 'null'  # ничего


@dataclass
class Relationship:
    id: ObjectId
    status: RelationStatus
    sender: ObjectId
    receiver: ObjectId

    def __init__(self, data):
        self.id = data['_id']
        self.status = RelationStatus(data['status'])
        self.sender = data['sender']
        self.receiver = data['receiver']

    def to_json(self):
        return json.dumps({"_id": str(self.id),
                           "status": self.status.value,
                           "sender": str(self.sender),
                           "receiver": str(self.receiver)
                           })
