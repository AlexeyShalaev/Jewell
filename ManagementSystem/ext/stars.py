import json
import logging
import time
from datetime import datetime, timedelta
from functools import wraps
from bs4 import BeautifulSoup

import requests

from ManagementSystem.ext.database.attendances import get_attendances
from ManagementSystem.ext.database.users import get_user_by_id

stars_path = './stars.json'


def get_stars_config():
    with open(stars_path) as f:
        return json.loads(f.read())


class StarsShtibel:
    def __init__(self, cookies, debug=False):
        self.__cookies = cookies
        self.__debug = debug

    def _request(self, uri, method):
        try:
            if self.__debug:
                print(f'{method.upper()}: {uri}')
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


stars = StarsShtibel(get_stars_config()['cookies'])


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


def update_stars_data(year, month):
    unprocessed_data = {
        'users': [],
        'lessons': []
    }
    try:
        stars_cfg = get_stars_config()
        stars_groups = stars_cfg['groups']
        stars_teachers = stars_cfg['teachers']
        attendances = [attendance
                       for attendance in get_attendances().data
                       if attendance.date.year == year and attendance.date.month == month]
        days = {}

        for i in attendances:
            day = i.date.day
            if day not in days:
                days[day] = {}
            r = get_user_by_id(i.user_id)
            if r.success:
                user = r.data
                stars_code = user.stars.code
                stars_group = user.stars.group
                if stars_code and stars_group and stars_group != 'null':
                    if stars_group not in days[day]:
                        days[day][stars_group] = []
                    days[day][stars_group].append(stars_code)
                else:
                    unprocessed_data['users'].append({
                        'id': str(user.id),
                        'last_name': user.last_name,
                        'first_name': user.first_name,
                        'code': stars_code,
                        'group': stars_group
                    })
        for day, groups in days.items():
            date = datetime(year, month, day)
            for group_key in groups:
                lesson_id = get_lesson_id(stars_groups[group_key], stars_teachers['Beinish Moshe-Boruch'], date)
                attempts_cnt = 0
                while lesson_id is None and attempts_cnt != 5:
                    create_lesson(stars_groups[group_key], stars_teachers['Beinish Moshe-Boruch'],
                                  date,
                                  19, 0,
                                  21, 0)
                    time.sleep(0.5)
                    lesson_id = get_lesson_id(stars_groups[group_key], stars_teachers['Beinish Moshe-Boruch'], date)
                    attempts_cnt += 1
                if lesson_id is None:
                    unprocessed_data['lessons'].append({
                        'group': stars_groups[group_key],
                        'date': date
                    })
                else:
                    mark_attendance(lesson_id, groups[group_key])
    except Exception as ex:
        logging.error(ex)
    return unprocessed_data
