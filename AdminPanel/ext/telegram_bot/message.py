import requests
from . import url


def send_message(text: str, chat_id: int):
    try:
        link = url + f'sendMessage?chat_id={chat_id}&text={text}'
        resp = requests.get(link)
    except Exception as ex:
        pass
