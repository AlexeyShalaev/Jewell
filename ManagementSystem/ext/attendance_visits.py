import logging
from datetime import timedelta

from ManagementSystem.ext.database.attendances import add_attendance
from ManagementSystem.ext.database.courses import get_courses_timetable
from ManagementSystem.ext.database.visits import get_visits_by_user_id, add_visit
from ManagementSystem.ext.models.userModel import Role, Reward
from ManagementSystem.ext.models.visit import VisitType
from ManagementSystem.ext.tools import has_element

COURSE_TIME = 2  # hours
VISIT_RANGE_MINUTES_30_MIN = 30 * 60  # seconds
VISIT_RANGE_MINUTES_15_MIN = 15 * 60  # seconds
NEXT_VISIT_MIN_TIME = 3600 * 1.5  # seconds


def handle_visit(user, date):
    timetable = get_courses_timetable()
    if user.role == Role.STUDENT and user.reward != Reward.NULL:
        visits = [visit
                  for visit in get_visits_by_user_id(user.id).data
                  if (date - visit.date).days < 1
                  and date.weekday() == visit.date.weekday()]
        visits.sort(key=lambda x: x.date, reverse=True)

        # поиск курсов по времени
        enter_courses = []
        exit_courses = []

        for i in timetable[date.weekday()]:
            start_time = date.replace(hour=i['hours'], minute=i['minutes'])
            end_time = start_time + timedelta(hours=COURSE_TIME)

            if (date < start_time and (
                    start_time - date).seconds < VISIT_RANGE_MINUTES_30_MIN) or (
                    date > start_time and (
                    date - start_time).seconds < VISIT_RANGE_MINUTES_15_MIN):
                enter_courses += i['courses']
                continue

            if (date < end_time and (
                    end_time - date).seconds < VISIT_RANGE_MINUTES_15_MIN) or (
                    date > end_time and (
                    date - end_time).seconds < VISIT_RANGE_MINUTES_30_MIN):
                exit_courses += i['courses']
                continue

        # поиск посещений
        last_exit = None
        last_enter = None
        for visit in visits:
            if last_exit is None and visit.visit_type == VisitType.EXIT:
                last_exit = visit
            elif last_enter is None and visit.visit_type == VisitType.ENTER:
                last_enter = visit
            elif last_enter and last_exit:
                break

        if exit_courses:
            for visit in visits:
                if visit.visit_type == VisitType.ENTER and has_element(exit_courses, visit.courses):
                    if last_exit is None or (date - last_exit.date).seconds >= NEXT_VISIT_MIN_TIME:
                        add_visit(user.id, date, VisitType.EXIT, visit.courses)
                        add_attendance(user.id, 1, date.strftime("%d.%m.%Y %H:%M:%S"))
                        return True, {"visit_type": VisitType.EXIT.value, "courses": visit.courses}
                    else:
                        logging.info(
                            f'[HANDLE VISIT] {user.phone_number}: не ушел, последний уход {last_exit.date.strftime("%d.%m.%Y %H:%M:%S")}')

        if enter_courses:
            if not visits:
                add_visit(user.id, date, VisitType.ENTER, enter_courses)
                return True, {"visit_type": VisitType.ENTER.value, "courses": enter_courses}
            else:
                if last_enter is None or (date - last_enter.date).seconds >= NEXT_VISIT_MIN_TIME:
                    add_visit(user.id, date, VisitType.ENTER, enter_courses)
                    return True, {"visit_type": VisitType.ENTER.value, "courses": enter_courses}
                else:
                    logging.info(
                        f'[HANDLE VISIT] {user.phone_number}: не пришел, последний вход {last_enter.date.strftime("%d.%m.%Y %H:%M:%S")}')
    else:
        return False, "У вас нет награды, обратитесь к администрации"

    return False, ""
