from ManagementSystem.ext.models.qr_code import *
from . import db, MongoDBResult


def add_qr_code(name, uri):
    db.qr_codes.insert_one({
        "name": name,
        "uri": uri
    })


def update_qr_code(id, key, value):
    db.qr_codes.update_one({'_id': ObjectId(id)}, {"$set": {key: value}})


def check_qr_code_by_id(id) -> bool:
    res = db.qr_codes.find_one({'_id': ObjectId(id)})
    if res:
        return True
    return False


def get_qr_codes() -> MongoDBResult:
    res = db.qr_codes.find()
    if res:
        qr_codes = []
        for i in list(res):
            qr_codes.append(QRCode(i))
        return MongoDBResult(True, qr_codes)
    else:
        return MongoDBResult(False, [])


def get_qr_code_by_id(id) -> MongoDBResult:
    r = db.qr_codes.find_one({'_id': ObjectId(id)})
    if r:
        return MongoDBResult(True, QRCode(r))
    else:
        return MongoDBResult(False, None)


def get_qr_code_by_name(name) -> MongoDBResult:
    r = db.qr_codes.find_one({'name': name})
    if r:
        return MongoDBResult(True, QRCode(r))
    else:
        return MongoDBResult(False, None)


def delete_qr_code(id):
    db.qr_codes.delete_one({
        '_id': ObjectId(id)
    })
