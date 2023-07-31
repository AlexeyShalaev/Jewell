import os

import logging
import requests

from ManagementSystem.ext import telegram_chat, directories
from . import url


def send_message(text: str, chat_id: int, parse_mode: str = 'html'):
    try:
        link = url + f'sendMessage?chat_id={chat_id}&text={text}&parse_mode={parse_mode}'
        resp = requests.get(link)
    except Exception as ex:
        logging.error(ex)


def send_news(text: str, filename=''):
    try:
        if filename == '':
            link = url + f'sendMessage?chat_id={telegram_chat}&text={text}'
            resp = requests.post(link)
        else:
            directory = directories['records']
            img = open(os.path.join(directory, filename), 'rb')
            link = url + f'sendPhoto?chat_id={telegram_chat}&caption={text}'
            resp = requests.post(link, files={'photo': img})
    except Exception as ex:
        logging.error(ex)


def send_file(document: str, chat_id: str):
    try:
        requests.post(f'{url}sendDocument', data={'chat_id': chat_id}, files={'document': open(document, 'rb')})
    except Exception as ex:
        logging.error(ex)
