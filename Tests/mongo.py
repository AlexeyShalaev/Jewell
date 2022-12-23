from AdminPanel.ext.database.attendances import *
from AdminPanel.ext.database.users import *
import random


def rand(mn=1, mx=2):
    return random.randint(mn, mx)


def test_attendance():
    user = get_user_by_phone_number("89854839731").data
    add_attendance(user.id, rand(), datetime.now())
