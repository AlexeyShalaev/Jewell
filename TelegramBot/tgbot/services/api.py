import requests

from TelegramBot.tgbot import links, jewell_token

attendance_url = f'{links.jewell}/api/attendance'


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
