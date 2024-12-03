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
                logging.info(f'{method.upper()}: {uri}')
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


@stars.get
def lesson_students(lesson_id):
    return (f'http://stars.shtibel.com/?pageView=managerAttendanceEdit'
            f'&row_id={lesson_id}')


# LESSONS

def parse_lessons_table(data, html, allowed_groups):
    soup = BeautifulSoup(html, 'html.parser')
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
            if date.day not in data:
                data[date.day] = {}
            if group not in data[date.day]:
                data[date.day][group] = []
            data[date.day][group].append({
                'code': cells[1].text,
                'time': cells[3].text,
                'teacher': cells[7].text,
            })
    return data


def get_lessons(year, month):
    logging.info(f"ATTENDANCE STARS EXPORT: getting lessons ({year}, {month})")
    data = dict()
    stars_cfg = get_stars_config()
    allowed_groups = stars_cfg['groups']
    resp = get_lessons_in_month(year, month)
    if resp.ok:
        logging.info(f"ATTENDANCE STARS EXPORT: resp OK")
        soup = BeautifulSoup(resp.text, 'html.parser')
        tmp = soup.find('select', class_='pagingSelect')
        if tmp is not None:
            logging.info(f"ATTENDANCE STARS EXPORT: pagingSelect is not None")
            pages = tmp.find_all('option')
            if len(pages) <= 1:
                logging.info(f"ATTENDANCE STARS EXPORT: 1 page")
                parse_lessons_table(data, resp.text, allowed_groups)
            else:
                logging.info(f"ATTENDANCE STARS EXPORT: {len(pages)} pages")
                for page in pages:
                    r = get_lessons_in_month(year, month, page=page.text)
                    if r.ok:
                        parse_lessons_table(data, r.text, allowed_groups)
    return data


def find_available_time_slots(needed_lessons_cnt, duration, existing_lessons):
    existing_slots = []

    # Преобразуем строки времени в объекты datetime
    for lesson in existing_lessons:
        start, end = lesson['time'].split("-")
        start_time = datetime.strptime(start, "%H:%M")
        end_time = datetime.strptime(end, "%H:%M")
        existing_slots.append((start_time, end_time))

    # Находим доступные временные слоты
    available_slots = []
    end_time = datetime.strptime("22:00", "%H:%M")

    while datetime.strptime("10:00", "%H:%M") <= end_time:
        start_time = end_time - timedelta(hours=duration)

        # Проверяем, не пересекаются ли временные слоты с существующими
        if all(end_time <= existing_start or start_time >= existing_end for existing_start, existing_end in
               existing_slots):
            time_slot = (start_time, end_time)
            available_slots.append(time_slot)
            existing_slots.append(time_slot)

        if len(available_slots) >= needed_lessons_cnt:
            break

        end_time -= timedelta(minutes=30)  # Переходим к следующему временному интервалу

    available_slots.sort(key=lambda slot: slot[1], reverse=True)
    return available_slots


def create_lessons(date, group, needed_lessons_cnt, existing_lessons):
    stars_cfg = get_stars_config()
    allowed_groups = stars_cfg['groups']
    stars_teachers = list(stars_cfg['teachers'].values())
    lesson_group = None

    if group in allowed_groups:
        lesson_group = allowed_groups[group]

    if lesson_group is None:
        return False, 'Unknown Group'

    duration = lesson_group['duration']
    slots = find_available_time_slots(needed_lessons_cnt, duration, existing_lessons)

    lessons_created = 0
    for i in range(needed_lessons_cnt):
        start_time, end_time = slots[i]
        resp = create_lesson(lesson_group['code'], random.choice(stars_teachers), date,
                             start_time.hour, start_time.minute,
                             end_time.hour, end_time.minute)
        if resp.ok:
            lessons_created += 1

        time.sleep(0.5)

    if lessons_created < needed_lessons_cnt:
        return False, f'{lessons_created}/{needed_lessons_cnt} lessons were created'

    return True, 'OK'


def mark_attendance_lesson(lesson_id, students_ids, delay=0.5):
    time.sleep(delay)
    resp = mark_attendance(lesson_id, students_ids)
    if resp.ok:
        return True, 'OK'
    return False, 'Failed'


def get_lesson_students(lesson_id):
    res = []
    resp = lesson_students(lesson_id)
    if resp.ok:
        soup = BeautifulSoup(resp.text, 'html.parser')
        table = soup.find('table', class_='boxTable')
        # Находим строки в таблице
        rows = table.find_all('tr')
        # Пропускаем заголовок (первую строку)
        for row in rows[1:]:
            # Получаем ячейки в текущей строке
            cells = row.find_all('td')
            # Извлекаем данные из ячеек
            student_code = cells[0]
            if cells[3].find_all('input', checked=True):
                res.append(student_code.text)
    return res
