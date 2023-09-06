from datetime import timedelta, datetime

from ManagementSystem.ext.database.attendances import add_attendance
from ManagementSystem.ext.database.courses import get_courses_timetable
from ManagementSystem.ext.database.visits import get_visits_by_user_id, add_visit
from ManagementSystem.ext.models.userModel import Role, Reward, Sex
from ManagementSystem.ext.models.visit import VisitType
from ManagementSystem.ext.tools import has_element

ONE_DAY = 24 * 60 * 60  # seconds
COURSE_TIME = 2  # hours
VISIT_RANGE_MINUTES = 30  # minutes
VISIT_RANGE_SECONDS = VISIT_RANGE_MINUTES * 60  # seconds
NEXT_VISIT_MIN_TIME = 3600 * 1.5  # seconds


def handle_visit(user, date):
    res = []

    timetable = get_courses_timetable()
    if user.role == Role.STUDENT and user.reward != Reward.NULL:
        visits = [visit
                  for visit in get_visits_by_user_id(user.id).data
                  if (date - visit.date).seconds < ONE_DAY
                  and date.weekday() == visit.date.weekday()]
        visits.sort(key=lambda x: x.date, reverse=True)

        # поиск курсов по времени
        enter_courses = []
        exit_courses = []

        for i in timetable[date.weekday()]:
            start_time = date.replace(hour=i['hours'], minute=i['minutes'])
            end_time = start_time + timedelta(hours=COURSE_TIME)

            if (date < start_time and (
                    start_time - date).seconds < VISIT_RANGE_SECONDS) or (
                    date > start_time and (
                    date - start_time).seconds < VISIT_RANGE_SECONDS):
                enter_courses += i['courses']
                continue

            if (date < end_time and (
                    end_time - date).seconds < VISIT_RANGE_SECONDS) or (
                    date > end_time and (
                    date - end_time).seconds < VISIT_RANGE_SECONDS):
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
                        res.append({"visit_type": VisitType.EXIT.value, "courses": visit.courses})
                    break

        if enter_courses:
            if not visits:
                add_visit(user.id, date, VisitType.ENTER, enter_courses)
                res.append({"visit_type": VisitType.ENTER.value, "courses": enter_courses})
            else:
                if (date - last_enter.date).seconds >= NEXT_VISIT_MIN_TIME:
                    add_visit(user.id, date, VisitType.ENTER, enter_courses)
                    res.append({"visit_type": VisitType.ENTER.value, "courses": enter_courses})

    return res
