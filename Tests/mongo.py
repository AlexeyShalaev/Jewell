from ManagementSystem.ext.database.attendances import *
from ManagementSystem.ext.database.users import *
import random


def rand(mn=1, mx=2):
    return random.randint(mn, mx)


def test_attendance():
    user = get_user_by_phone_number("89854839731").data
    add_attendance(user.id, 1, "15.09.2022 21:00:00")
    add_attendance(user.id, 1, "22.09.2022 21:00:00")
    add_attendance(user.id, 1, "25.09.2022 21:00:00")
    add_attendance(user.id, 1, "29.09.2022 21:00:00")
    add_attendance(user.id, 1, "06.10.2022 21:00:00")
    add_attendance(user.id, 1, "13.10.2022 21:00:00")
    add_attendance(user.id, 1, "20.10.2022 21:00:00")
    add_attendance(user.id, 1, "27.10.2022 21:00:00")
    add_attendance(user.id, 1, "03.11.2022 21:00:00")
    add_attendance(user.id, 1, "10.11.2022 21:00:00")
    add_attendance(user.id, 1, "17.11.2022 21:00:00")
    add_attendance(user.id, 1, "24.11.2022 21:00:00")
    add_attendance(user.id, 1, "01.12.2022 21:00:00")
    add_attendance(user.id, 1, "08.12.2022 21:00:00")



def change_reward():
    user = get_user_by_phone_number("89854839731").data
    update_user(user.id, "reward", Reward.TRIP.value)
