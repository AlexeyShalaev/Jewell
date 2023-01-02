import requests
from . import url
from ManagementSystem.ext import telegram_chat


def send_message(text: str, chat_id: int):
    try:
        link = url + f'sendMessage?chat_id={chat_id}&text={text}'
        resp = requests.get(link)
    except Exception as ex:
        pass


def send_news(text: str):
    try:
        link = url + f'sendMessage?chat_id={telegram_chat}&text={text}'
        resp = requests.get(link)
    except Exception as ex:
        pass
