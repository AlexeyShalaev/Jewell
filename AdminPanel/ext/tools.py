import datetime
import random


def get_random_color():
    random_number = random.randint(0, 16777215)
    hex_number = str(hex(random_number))
    hex_number = '#' + hex_number[2:]
    return hex_number


def get_month(m: int) -> str:
    if m == 1:
        return "Янв"
    elif m == 2:
        return "Фев"
    elif m == 3:
        return "Март"
    elif m == 4:
        return "Апр"
    elif m == 5:
        return "Май"
    elif m == 6:
        return "Июнь"
    elif m == 7:
        return "Июль"
    elif m == 8:
        return "Авг"
    elif m == 9:
        return "Сент"
    elif m == 10:
        return "Окт"
    elif m == 11:
        return "Нояб"
    elif m == 12:
        return "Дек"

