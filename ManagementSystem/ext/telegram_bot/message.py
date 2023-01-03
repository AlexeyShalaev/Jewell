import requests

from ManagementSystem.ext import telegram_chat
from . import url


def send_message(text: str, chat_id: int):
    try:
        link = url + f'sendMessage?chat_id={chat_id}&text={text}'
        resp = requests.get(link)
    except Exception as ex:
        pass


def send_news(text: str, filename=''):
    try:
        if filename == '':
            link = url + f'sendMessage?chat_id={telegram_chat}&text={text}'
            resp = requests.post(link)
        else:
            directory = 'storage/records/'
            img = open(directory+filename, 'rb')
            link = url + f'sendPhoto?chat_id={telegram_chat}&caption={text}'
            resp = requests.post(link, files={'photo': img})
    except Exception as ex:
        pass
