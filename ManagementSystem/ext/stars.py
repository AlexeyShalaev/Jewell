import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from bs4 import BeautifulSoup

import requests

stars_path = './stars.json'


def get_stars_config():
    with open(stars_path) as f:
        return json.loads(f.read())


stars_cfg = get_stars_config()


class StarsShtibel:
    def __init__(self, cookies):
        self.__cookies = cookies

    def _request(self, uri, method):
        try:
            if method == 'get':
                r = requests.get(uri, cookies=self.__cookies)
            elif method == 'post':
                r = requests.post(uri, cookies=self.__cookies)
            else:
                raise Exception('Unknown request method')
            return r
        except Exception as ex:
            logging.error(f'Exception: {ex}')
            return None

    def get(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            uri = func(*args, **kwargs)
            return self._request(uri, 'get')

        return wrapper

    def post(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            uri = func(*args, **kwargs)
            return self._request(uri, 'post')

        return wrapper


stars = StarsShtibel(stars_cfg['cookies'])


@stars.get
def create_lesson(group_id, teacher_id, date, start_hour, start_minute, end_hour, end_minute):
    lesson_date = date.strftime("%d/%m/%Y")
    return (f'http://stars.shtibel.com/?pageView=managerLessonNew'
            f'&action=save'
            f'&group_id={group_id}'
            f'&teacher_id={teacher_id}'
            f'&lesson_name={lesson_date}'
            f'&lesson_date={lesson_date}'
            f'&start_hour={start_hour}'
            f'&start_minute={start_minute}'
            f'&end_hour={end_hour}'
            f'&end_minute={end_minute}')


@stars.get
def get_lesson(group_id, teacher_id, date):
    lesson_date = date.strftime("%d/%m/%Y")
    return (f'http://stars.shtibel.com/?pageView=managerLessonList'
            f'&action=filter'
            f'&group_id={group_id}'
            f'&teacher_id={teacher_id}'
            f'&lesson_date_start={lesson_date}'
            f'&lesson_date_end={lesson_date}'
            )


def get_lesson_id(group_id, teacher_id, date):
    r = get_lesson(group_id,
                   teacher_id,
                   date)
    if r.ok:
        soup = BeautifulSoup(r.text, 'lxml')
        table = soup.find('table', class_='tableList')

        # Находим строки в таблице
        rows = table.find_all('tr')

        # Пропускаем заголовок (первую строку)
        for row in rows[1:]:
            # Получаем ячейки в текущей строке
            cells = row.find_all('td')
            # Извлекаем данные из ячеек
            code = cells[1].text
            return code
    return None


@stars.get
def get_lessons_in_month(year, month):
    # Получаем первый день месяца
    first_day_of_month = datetime(year, month, 1)
    # Вычисляем последний день месяца
    if month == 12:
        next_month = datetime(year + 1, 1, 1)
    else:
        next_month = datetime(year, month + 1, 1)
    last_day_of_month = next_month - timedelta(days=1)

    return (f'http://stars.shtibel.com/?pageView=managerLessonList'
            f'&action=filter'
            f'&lesson_date_start={first_day_of_month.strftime("%d/%m/%Y")}'
            f'&lesson_date_end={last_day_of_month.strftime("%d/%m/%Y")}'
            )


@stars.get
def mark_attendance(lesson_id, students_ids):
    uri = (f'http://stars.shtibel.com/?pageView=managerAttendanceEdit'
           f'&row_id={lesson_id}'
           f'&action=save')
    for student_id in students_ids:
        uri += f'&attendance_{student_id}=1'
    return uri
