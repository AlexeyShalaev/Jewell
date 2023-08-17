from bson import ObjectId


class QRCode:
    id: ObjectId  # ID
    name: str  # название
    uri: str

    def __init__(self, data):
        self.id = data['_id']
        self.name = data['name']
        self.uri = data['uri']
