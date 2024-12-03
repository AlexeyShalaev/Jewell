import logging

import requests

from TelegramBot.tgbot import links, jewell_token

animation_url = f'{links.server}/api/animation'
attendance_url = f'{links.server}/api/attendance'
snapshot_url = f'{links.server}/api/snapshot'
stars_url = f'{links.server}/api/stars'


def get_admin_attendance() -> (bool, ...):
    try:
        r = requests.post(f'{attendance_url}/admin', json={"token": jewell_token})
        if r.ok:
            res = r.json()
            if res['success']:
                return True, res['data']
    except Exception as ex:
        logging.error(ex)
    return False, None


def get_student_attendance(user_id) -> (bool, ...):
    try:
        r = requests.post(f'{attendance_url}/student', json={"token": jewell_token, "user_id": user_id})
        if r.ok:
            res = r.json()
            if res['success']:
                return True, res['data']
    except Exception as ex:
        logging.error(ex)
    return False, None


def snapshot_dump(chat_id: int) -> bool:
    try:
        r = requests.post(f'{snapshot_url}/dump', json={"token": jewell_token, "chat_id": chat_id})
        if r.ok:
            res = r.json()
            return res['success']
    except Exception as ex:
        logging.error(ex)
    return False


def snapshot_restore(filename: str) -> bool:
    try:
        r = requests.post(f'{snapshot_url}/restore', json={"token": jewell_token, "file": filename})
        if r.ok:
            res = r.json()
            return res['success']
    except Exception as ex:
        logging.error(ex)
    return False


def snapshot_backups() -> (bool, ...):
    try:
        r = requests.post(f'{snapshot_url}/backups', json={"token": jewell_token})
        if r.ok:
            res = r.json()
            if res['success']:
                return True, res['files']
    except Exception as ex:
        logging.error(ex)
    return False, None


def animation_add(user_id, file, file_extension) -> bool:
    try:
        r = requests.post(f'{animation_url}/add',
                          data={"token": jewell_token, "user_id": user_id, "file_extension": file_extension},
                          files={'file': file.read()})
        if r.ok:
            res = r.json()
            return res['success']
    except Exception as ex:
        print(ex)
        logging.error(ex)
    return False


def stars_export_attendance(month: int) -> (bool, str):
    try:
        r = requests.post(f'{stars_url}/month/export', json={"token": jewell_token, "month": month}, timeout=300)
        res = r.json()
        return res["success"], res["info"]
    except Exception as ex:
        logging.error(ex)
        return False, str(ex)