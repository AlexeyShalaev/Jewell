import requests

from TelegramBot.tgbot import links, jewell_token

attendance_url = f'{links.jewell}/api/attendance'
snapshot_url = f'{links.jewell}/api/snapshot'


def get_admin_attendance() -> (bool, ...):
    try:
        r = requests.post(f'{attendance_url}/admin', json={"token": jewell_token})
        if r.ok:
            res = r.json()
            if res['success']:
                return True, res['data']
    except:
        pass
    return False, None


def get_student_attendance(user_id) -> (bool, ...):
    try:
        r = requests.post(f'{attendance_url}/student', json={"token": jewell_token, "user_id": user_id})
        if r.ok:
            res = r.json()
            if res['success']:
                return True, res['data']
    except:
        pass
    return False, None


def snapshot_dump(chat_id: int) -> bool:
    try:
        r = requests.post(f'{snapshot_url}/dump', json={"token": jewell_token, "chat_id": chat_id})
        if r.ok:
            res = r.json()
            return res['success']
    except:
        pass
    return False


def snapshot_restore(filename: str) -> bool:
    try:
        r = requests.post(f'{snapshot_url}/restore', json={"token": jewell_token, "file": filename})
        if r.ok:
            res = r.json()
            return res['success']
    except:
        pass
    return False


def snapshot_backups() -> (bool, ...):
    try:
        r = requests.post(f'{snapshot_url}/backups', json={"token": jewell_token})
        if r.ok:
            res = r.json()
            if res['success']:
                return True, res['files']
    except:
        pass
    return False, None
