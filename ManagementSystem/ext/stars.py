import json
import logging
import random
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


stars = StarsShtibel(get_stars_config()['cookies'], debug=True)


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
def get_lesson(group_id, date):
    lesson_date = date.strftime("%d/%m/%Y")
    return (f'http://stars.shtibel.com/?pageView=managerLessonList'
            f'&action=filter'
            f'&group_id={group_id}'
            f'&lesson_date_start={lesson_date}'
            f'&lesson_date_end={lesson_date}'
            )


@stars.get
def get_lessons_in_month(year, month, page=None):
    # Получаем первый день месяца
    first_day_of_month = datetime(year, month, 1)
    # Вычисляем последний день месяца
    if month == 12:
        next_month = datetime(year + 1, 1, 1)
    else:
        next_month = datetime(year, month + 1, 1)
    last_day_of_month = next_month - timedelta(days=1)

    if page is None:
        return (f'http://stars.shtibel.com/?pageView=managerLessonList'
                f'&action=filter'
                f'&lesson_date_start={first_day_of_month.strftime("%d/%m/%Y")}'
                f'&lesson_date_end={last_day_of_month.strftime("%d/%m/%Y")}'
                )

    return (f'http://stars.shtibel.com/?pageView=managerLessonList'
            f'&iCurrentPage={page}'
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


# LESSONS

def parse_lessons_table(data, html, allowed_groups):
    soup = BeautifulSoup(html, 'lxml')
    table = soup.find('table', class_='tableList')
    # Находим строки в таблице
    rows = table.find_all('tr')
    # Пропускаем заголовок (первую строку)
    for row in rows[1:]:
        # Получаем ячейки в текущей строке
        cells = row.find_all('td')
        # Извлекаем данные из ячеек

        group = cells[5].text
        if group in allowed_groups:
            date = datetime.strptime(cells[2].text, "%m/%d/%Y")
            reward = allowed_groups[group]['reward']
            if date.day not in data:
                data[date.day] = {}
            if reward not in data[date.day]:
                data[date.day][reward] = []
            data[date.day][reward].append({
                'code': cells[1].text,
                'time': cells[3].text,
                'teacher': cells[7].text,
            })
    return data


def get_lessons(year, month):
    """
    data = dict()
    stars_cfg = get_stars_config()
    allowed_groups = stars_cfg['groups']
    resp = get_lessons_in_month(year, month)
    if resp.ok:
        soup = BeautifulSoup(resp.text, 'lxml')
        pages = soup.find('select', class_='pagingSelect').find_all('option')
        if len(pages) <= 1:
            parse_lessons_table(data, resp.text, allowed_groups)
        else:
            for page in pages:
                r = get_lessons_in_month(year, month, page=page.text)
                if r.ok:
                    parse_lessons_table(data, r.text, allowed_groups)
    """
    data = {28: {'grant': [{'code': '105904', 'time': '19:30-21:30', 'teacher': 'Weissberg Mordechai '}],
                 'trip': [{'code': '105934', 'time': '19:00-21:00', 'teacher': 'Weissberg Mordechai '}]},
            27: {'trip': [{'code': '105935', 'time': '19:00-21:00', 'teacher': 'Beinish Moshe-Boruch'}],
                 'grant': [{'code': '105903', 'time': '19:30-21:30', 'teacher': 'Lastov  Isheyahu'}]},
            26: {'grant': [{'code': '105902', 'time': '19:30-21:30', 'teacher': 'Beinish Moshe-Boruch'}],
                 'trip': [{'code': '105936', 'time': '19:00-21:00', 'teacher': 'Lastov  Isheyahu'}]},
            25: {'trip': [{'code': '105937', 'time': '20:00-22:00', 'teacher': 'Feldman Yonatan'}]},
            24: {'grant': [{'code': '105897', 'time': '13:00-15:00', 'teacher': 'Beinish Moshe-Boruch'}],
                 'trip': [{'code': '105993', 'time': '13:00-15:00', 'teacher': 'Beinish Moshe-Boruch'}]},
            21: {'grant': [{'code': '105901', 'time': '19:30-21:30', 'teacher': 'Lastov  Isheyahu'}],
                 'trip': [{'code': '105938', 'time': '19:00-21:00', 'teacher': 'Lastov  Isheyahu'}]},
            20: {'trip': [{'code': '105939', 'time': '19:00-21:00', 'teacher': 'Weissberg Mordechai '}],
                 'grant': [{'code': '105900', 'time': '19:30-21:30', 'teacher': 'Lakshin Alexandr'}]},
            19: {'grant': [{'code': '105899', 'time': '19:30-21:30', 'teacher': 'Feldman Yonatan'}],
                 'trip': [{'code': '105990', 'time': '19:00-21:00', 'teacher': 'Lakshin Alexandr'}]},
            18: {'trip': [{'code': '105987', 'time': '19:00-21:00', 'teacher': 'Beinish Moshe-Boruch'}],
                 'grant': [{'code': '105898', 'time': '19:30-21:30', 'teacher': 'Beinish Moshe-Boruch'}]},
            17: {'trip': [{'code': '105988', 'time': '20:00-22:00', 'teacher': 'Lastov  Isheyahu'}]},
            14: {'trip': [{'code': '105985', 'time': '19:00-21:00', 'teacher': 'Feldman Yonatan'}],
                 'grant': [{'code': '105896', 'time': '19:30-21:30', 'teacher': 'Lastov  Isheyahu'}]},
            13: {'grant': [{'code': '105895', 'time': '19:30-21:30', 'teacher': 'Lakshin Alexandr'}],
                 'trip': [{'code': '105986', 'time': '19:00-21:00', 'teacher': 'Lakshin Alexandr'}]},
            12: {'grant': [{'code': '105894', 'time': '19:30-21:30', 'teacher': 'Feldman Yonatan'}],
                 'trip': [{'code': '105954', 'time': '19:00-21:00', 'teacher': 'Beinish Moshe-Boruch'}]},
            11: {'trip': [{'code': '105955', 'time': '19:00-21:00', 'teacher': 'Weissberg Mordechai '}],
                 'grant': [{'code': '105888', 'time': '19:30-21:30', 'teacher': 'Beinish Moshe-Boruch'}]},
            10: {'grant': [{'code': '105887', 'time': '13:00-15:00', 'teacher': 'Weissberg Mordechai '}],
                 'trip': [{'code': '105956', 'time': '13:00-15:00', 'teacher': 'Lastov  Isheyahu'}]},
            7: {'trip': [{'code': '105957', 'time': '19:00-21:00', 'teacher': 'Feldman Yonatan'}],
                'grant': [{'code': '105893', 'time': '19:30-20:30', 'teacher': 'Lastov  Isheyahu'}]},
            6: {'grant': [{'code': '105892', 'time': '19:30-21:30', 'teacher': 'Lakshin Alexandr'}],
                'trip': [{'code': '105958', 'time': '19:00-21:00', 'teacher': 'Weissberg Mordechai '}]},
            5: {'grant': [{'code': '105891', 'time': '19:30-21:30', 'teacher': 'Feldman Yonatan'}],
                'trip': [{'code': '105952', 'time': '19:00-21:00', 'teacher': 'Lakshin Alexandr'}]},
            4: {'trip': [{'code': '105953', 'time': '19:00-21:00', 'teacher': 'Beinish Moshe-Boruch'}],
                'grant': [{'code': '105890', 'time': '19:30-21:30', 'teacher': 'Beinish Moshe-Boruch'}]}}
    data = {28: {'grant': [{'code': '105904', 'time': '19:30-21:30', 'teacher': 'Weissberg Mordechai '}],
                 'trip': [{'code': '105934', 'time': '19:00-21:00', 'teacher': 'Weissberg Mordechai '}]},
            27: {'trip': [{'code': '105935', 'time': '19:00-21:00', 'teacher': 'Beinish Moshe-Boruch'}],
                 'grant': [{'code': '105903', 'time': '19:30-21:30', 'teacher': 'Lastov  Isheyahu'}]},
            26: {'grant': [{'code': '105902', 'time': '19:30-21:30', 'teacher': 'Beinish Moshe-Boruch'}],
                 'trip': [{'code': '105936', 'time': '19:00-21:00', 'teacher': 'Lastov  Isheyahu'}]},
            }
    return data
