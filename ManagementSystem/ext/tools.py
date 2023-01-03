import logging
import queue
import random
import re
from datetime import datetime

import requests

from ManagementSystem.ext.crypt import encrypt_id_with_no_digits
from ManagementSystem.ext.database.relationships import get_relationships, RelationStatus
from ManagementSystem.ext.database.users import get_user_by_id, MongoDBResult

logger = logging.getLogger(__name__)  # logging


def normal_phone_number(phone_number: str) -> str:
    # функция возвращает номер телефона в формате 8XXXXXXXXXX
    phone_number = re.sub(r'[ ()-]', '', phone_number)
    phone_number = phone_number.replace('+7', '8', 1)
    if phone_number.startswith('7'):
        phone_number = phone_number.replace('7', '8', 1)
    return phone_number


def get_random_color():
    random_number = random.randint(0, 16777215)
    hex_number = str(hex(random_number))
    hex_number = '#' + hex_number[2:]
    return hex_number


def get_month(m: int, short: bool = True) -> str:
    if m == 1:
        return "Янв" if short else "января"
    elif m == 2:
        return "Фев" if short else "февраля"
    elif m == 3:
        return "Март" if short else "марта"
    elif m == 4:
        return "Апр" if short else "апреля"
    elif m == 5:
        return "Май" if short else "мая"
    elif m == 6:
        return "Июнь" if short else "июня"
    elif m == 7:
        return "Июль" if short else "июля"
    elif m == 8:
        return "Авг" if short else "августа"
    elif m == 9:
        return "Сент" if short else "сентября"
    elif m == 10:
        return "Окт" if short else "октября"
    elif m == 11:
        return "Нояб" if short else "ноября"
    elif m == 12:
        return "Дек" if short else "декабря"
    else:
        return str(m)


def set_records(resp: MongoDBResult, sort=True) -> list:
    records = []
    if resp.success:
        if sort:
            recs = sorted(resp.data, key=lambda record: record.time, reverse=True)
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
                        'time': rec.time.strftime("%d.%m.%Y %H:%M:%S")
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


def get_friends(sui: str) -> list:
    friends = []
    resp = get_relationships()
    if resp.success:
        for req in resp.data:
            if req.status == RelationStatus.ACCEPTED:
                if str(req.receiver) == sui:
                    friends.append(str(req.sender))
                elif str(req.sender) == sui:
                    friends.append(str(req.receiver))
    return friends


def bfs(s, t, users):
    try:
        dist = dict()
        p = dict()
        adj = dict()
        for user in users:
            sui = str(user.id)
            dist[sui] = len(users)
            p[sui] = -1
            adj[sui] = get_friends(sui)

        dist[s] = 0
        q = queue.Queue()
        q.put(s)
        while not q.empty():
            v = q.get()
            for u in adj[v]:
                if dist[u] > dist[v] + 1:
                    p[u] = v
                    dist[u] = dist[v] + 1
                    q.put(u)
        if dist[t] == len(users):
            return []
        path = []
        while t != -1:
            path.append(t)
            t = p[t]

        path.reverse()
        return path
    except Exception:
        return []


def shabbat(geo_name_id: int = 524901) -> dict:
    # https://www.hebcal.com/home/197/shabbat-times-rest-api
    url = f'https://www.hebcal.com/shabbat?cfg=json&geonameid={geo_name_id}'
    res = {"candle": "", "havdalah": ""}
    try:
        request = requests.get(url)
        if request.ok:
            for i in request.json()['items']:
                try:
                    title = i['title']
                    date = i['date']
                    if "T" in date:
                        if "+" in date:
                            date = datetime.strptime(date[:date.index('+')], '%Y-%m-%dT%H:%M:%S')
                        else:
                            date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
                    else:
                        date = datetime.strptime(date, '%Y-%m-%d')
                    if title.startswith('Candle'):
                        res['candle'] = f'{date.day} {get_month(date.month, False)} в {date.hour}:{date.minute}'
                    elif title.startswith('Havdalah'):
                        res['havdalah'] = f'{date.day} {get_month(date.month, False)} в {date.hour}:{date.minute}'
                except Exception:
                    pass
    except Exception as ex:
        logger.error(ex)
    return res
