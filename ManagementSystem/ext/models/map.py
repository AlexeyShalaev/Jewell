from dataclasses import dataclass
from bson import ObjectId
from datetime import datetime
import json


@dataclass
class Map:
    id: ObjectId  # ID офера
    name: str  # название карты
    countries: list  # страны

    def __init__(self, data):
        self.id = data['_id']
        self.name = data['name']
        self.countries = data['countries']

    def to_json(self):
        return json.dumps({"_id": str(self.id),
                           "name": self.name,
                           "countries": self.countries
                           })
