import random
from AdminPanel.ext.database.records import *
from AdminPanel.ext.database.relationships import *
from AdminPanel.ext.crypt import *


def get_random_color():
    random_number = random.randint(0, 16777215)
    hex_number = str(hex(random_number))
    hex_number = '#' + hex_number[2:]
    return hex_number


def get_month(m: int) -> str:
    if m == 1:
        return "Янв"
    elif m == 2:
        return "Фев"
    elif m == 3:
        return "Март"
    elif m == 4:
        return "Апр"
    elif m == 5:
        return "Май"
    elif m == 6:
        return "Июнь"
    elif m == 7:
        return "Июль"
    elif m == 8:
        return "Авг"
    elif m == 9:
        return "Сент"
    elif m == 10:
        return "Окт"
    elif m == 11:
        return "Нояб"
    elif m == 12:
        return "Дек"


def set_records(resp: MongoDBResult, sort=True) -> list:
    records = []
    if resp.success:
        if sort:
            recs = sorted(resp.data, key=lambda rec: rec.time, reverse=True)
        else:
            recs = resp.data
        for rec in recs:
            r = get_user_by_id(rec.author)
            if r.success:
                author = r.data
                record_status, record_id = encrypt_id_with_no_digits(str(rec.id))
                if record_status:
                    records.append({
                        'record_id': f'{record_id}',
                        'user_id': f'{author.id}',
                        'author': f'{author.first_name} {author.last_name}',
                        'text': rec.text,
                        'time': rec.time.strftime("%m.%d.%Y %H:%M:%S")
                    })
    return records


def set_relations(current_user):
    friends = []
    friends_requests_to = []
    friends_requests_from = []
    resp = get_relationships()
    if resp.success:
        for req in resp.data:
            if req.status == RelationStatus.SUBMITTED:
                if str(req.receiver) == str(current_user.id):
                    r = get_user_by_id(req.sender)
                    if r.success:
                        sender = r.data
                        s, v = encrypt_id_with_no_digits(str(req.id))
                        friends_requests_to.append({
                            'id': v,
                            'sender_id': sender.id,
                            'first_name': sender.first_name,
                            'last_name': sender.last_name,
                        })
                elif str(req.sender) == str(current_user.id):
                    r = get_user_by_id(req.receiver)
                    if r.success:
                        receiver = r.data
                        s, v = encrypt_id_with_no_digits(str(req.id))
                        friends_requests_from.append({
                            'id': v,
                            'receiver_id': receiver.id,
                            'first_name': receiver.first_name,
                            'last_name': receiver.last_name,
                        })
            elif req.status == RelationStatus.ACCEPTED:
                r = MongoDBResult(False, None)
                if str(req.receiver) == str(current_user.id):
                    r = get_user_by_id(req.sender)
                elif str(req.sender) == str(current_user.id):
                    r = get_user_by_id(req.receiver)
                if r.success:
                    friend = r.data
                    s, v = encrypt_id_with_no_digits(str(req.id))
                    friends.append({
                        'id': v,
                        'friend': friend
                    })
    return friends, friends_requests_to, friends_requests_from
