import time
import logging

from Assistant import links
from Assistant.MongoDB.users import get_users_by_role
from Assistant.ext.terminal import get_website_status, restart_website
from Assistant.models.userModel import Role
from Assistant.telegram.message import send_message


def check_website(attempts=10):
    try:
        for i in range(attempts):
            if get_website_status():
                return
            restart_website()
            time.sleep(1)
        admins = get_users_by_role(Role.ADMIN).data
        for admin in admins:
            if admin.telegram_id is not None:
                send_message(f'Сайт {links.jewell} не работает. Не удалось перезапустить после {attempts} попыток.',
                             admin.telegram_id)
    except Exception as ex:
        logging.error(ex)
