from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from datetime import datetime

from ManagementSystem.ext.database.attendances import get_filtered_attendances
from ManagementSystem.ext.database.users import get_user_by_id
from ManagementSystem.ext.models.userModel import Reward
from ManagementSystem.ext.stars import get_lessons, get_lesson_students


def process_attendance(attendance, bad_users, days, chosen_month):
    day = attendance.date.day
    if day not in days:
        days[day] = {
            'students': {},
            'max_attendances': {},
            'date': datetime(attendance.date.year, chosen_month, day).strftime("%d.%m.%Y"),
            'lessons': {}
        }
    r = get_user_by_id(attendance.user_id)
    if r.success:
        user = r.data
        if user.reward in (Reward.TRIP, Reward.GRANT):
            user_name = f'{user.last_name} {user.first_name}'
            if not user.stars.code:
                bad_users['code'].add(attendance.user_id)
            else:
                if user.stars.group not in days[day]['students']:
                    days[day]['students'][user.stars.group] = {}
                    days[day]['max_attendances'][user.stars.group] = 0
                if user.stars.code not in days[day]['students'][user.stars.group]:
                    days[day]['students'][user.stars.group][user.stars.code] = {
                        'user_id': str(attendance.user_id),
                        'name': user_name,
                        'count': 0,
                        'exported_attendance': 0
                    }
                days[day]['students'][user.stars.group][user.stars.code]['count'] += 1
                days[day]['max_attendances'][user.stars.group] = max(
                    days[day]['max_attendances'][user.stars.group],
                    days[day]['students'][user.stars.group][user.stars.code]['count']
                )
        else:
            bad_users['reward'].add(attendance.user_id)
    else:
        bad_users['database'].add(attendance.user_id)


def get_stars_export_data(month):
    logging.info(f"ATTENDANCE STARS EXPORT: {month}")

    now = datetime.now()
    chosen_month = int(month)
    if now.month >= 9:
        start = now.year
        end = start + 1
    else:
        end = now.year
        start = end - 1

    gl_year = start if chosen_month >= 9 else end
    attendances = get_filtered_attendances(chosen_month, gl_year)

    bad_users = {'database': set(), 'reward': set(), 'code': set()}
    days = {}

    # Многопоточность для обработки посещений
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(process_attendance, attendance, bad_users, days, chosen_month)
            for attendance in attendances
        ]
        for future in as_completed(futures):
            future.result()  # Если требуется обработка ошибок, добавить try/except

    for day, lessons in get_lessons(gl_year, chosen_month).items():
        if day in days:
            days[day]['lessons'] = lessons

    # Сортировка и обработка данных остаются неизменными
    for day_data in days.values():
        days_students = day_data['students']
        for category in days_students:
            days_students[category] = dict(sorted(days_students[category].items()))

        days_lessons = day_data['lessons']
        for category in days_lessons:
            days_lessons[category] = sorted(days_lessons[category],
                                            key=lambda x: int(x['time'].split('-')[1].split(':')[0]), reverse=True)

    lessons_to_create = []
    for day, data in days.items():
        for group, students in data['students'].items():
            lessons_exists = len(data['lessons'].get(group, []))
            if lessons_exists < data['max_attendances'][group]:
                lessons_to_create.append({
                    'date': data['date'],
                    'group': group,
                    'count': data['max_attendances'][group] - lessons_exists
                })
    lessons_to_create.sort(key=lambda x: (x['date'], x['group'], x['count']))

    if len(lessons_to_create) == 0:
        for day, data in days.items():
            for group, lessons in data['lessons'].items():
                for lesson in lessons:
                    lesson['students'] = {}
                    checked_students = get_lesson_students(lesson['code'])
                    for student_code, student in data['students'][group].items():
                        if student['exported_attendance'] < student['count']:
                            student['exported_attendance'] += 1
                            lesson['students'][student_code] = {
                                'name': student['name'],
                                'user_id': student['user_id'],
                                'checked': 0,
                            }
                            if student_code in checked_students:
                                lesson['students'][student_code]['checked'] = 1
                    lesson['students'] = dict(sorted(lesson['students'].items(), key=lambda x: x[1]['name']))

    return days, lessons_to_create, bad_users
