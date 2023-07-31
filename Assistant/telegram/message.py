import requests
import logging

from . import url


def send_message(text: str, chat_id: int, parse_mode: str = 'html'):
    try:
        link = url + f'sendMessage?chat_id={chat_id}&text={text}&parse_mode={parse_mode}'
        resp = requests.get(link)
    except Exception as ex:
        logging.error(ex)
