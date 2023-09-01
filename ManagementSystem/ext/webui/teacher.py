import os
import re
from datetime import datetime
import logging

from flask import *
from flask_login import *
from flask_toastr import *

from ManagementSystem.ext import directories, valid_images, system_variables
from ManagementSystem.ext.crypt import encrypt_id_with_no_digits
from ManagementSystem.ext.database.attendances import add_attendance_marker, get_attendance_markers, \
    update_attendance_marker, delete_attendance_marker, add_attendance, get_attendance_marker_by_id, delete_attendance, \
    update_attendance, get_attendances_by_user_id
from ManagementSystem.ext.database.courses import get_courses_by_teacher
from ManagementSystem.ext.database.maps import get_map_by_name
from ManagementSystem.ext.database.records import get_records_by_author, get_records_by_type, RecordType, add_record, \
    update_record_news, delete_record
from ManagementSystem.ext.database.users import get_user_by_id, get_users, get_users_by_role
from ManagementSystem.ext.logistics import auto_redirect, check_session
from ManagementSystem.ext.models.userModel import Role, Reward
from ManagementSystem.ext.telegram.message import send_news
from ManagementSystem.ext.tools import shabbat, get_random_color, set_records, get_friends, rus2eng

teacher = Blueprint('teacher', __name__, url_prefix='/teacher', template_folder='templates/teacher',
                    static_folder='assets')


# Уровень:              Главная страница
# База данных:          User
# HTML:                 home
@teacher.route('/')
@teacher.route('/home', methods=['POST', 'GET'])
@login_required
def teacher_home():
    # auto redirect
    status, url = auto_redirect(ignore_role=Role.TEACHER)
    if status:
        return redirect(url)
    # check session
    if not check_session():
        logout_user()
        return redirect(url_for("view.landing"))
    trip_map = {"values": {}, "colors": {}}
    resp = get_map_by_name(name='trips')
    if resp.success:
        countries = resp.data.countries
        for i in range(len(countries)):
            trip_map["values"][countries[i]] = i + 1
            trip_map["colors"][str(i + 1)] = get_random_color()
    return render_template("teacher/home.html", shabbat=shabbat(),
                           news=set_records(get_records_by_type(RecordType.NEWS)),
                           map=trip_map)


# Уровень:              news
# База данных:          User
# HTML:                 news
@teacher.route('/news', methods=['POST', 'GET'])
@login_required
def teacher_news():
    # auto redirect
    status, url = auto_redirect(ignore_role=Role.TEACHER)
    if status:
        return redirect(url)
    # check session
    if not check_session():
        logout_user()
        return redirect(url_for("view.landing"))

    if request.method == "POST":
        try:
            if request.form['btn_news'] == 'add_record':
                record_text = request.form.get("input_text")
                lifetime = request.form.get("input_lifetime")
                send_in_telegram = request.form.get("input_telegram")

                if lifetime == 'Никогда':
                    lifetime = 0
                elif lifetime == 'День':
                    lifetime = 1
                elif lifetime == 'Неделя':
                    lifetime = 7
                else:
                    lifetime = int(lifetime)
                    if lifetime < 0 or lifetime > 365:
                        flash('Число дней может быть от 0 до 365.', 'warning')
                        return redirect(url_for('teacher.teacher_news'))

                inserted_record = add_record(current_user.id, record_text, datetime.now(), type=RecordType.NEWS,
                                             lifetime=lifetime)
                flash('Вы добавили новость.', 'success')

                # image
                filename = ''
                try:
                    image = request.files['record_image']
                    img_type = image.filename.split('.')[-1].lower()
                    if img_type != '':
                        if img_type in valid_images:
                            resp_status, data = encrypt_id_with_no_digits(str(inserted_record.inserted_id))
                            record_id = data
                            directory = directories['records']
                            files = os.listdir(directory)
                            for file in files:
                                if record_id == file.split('.')[0]:
                                    filename = file
                                    break
                            if filename != '':
                                os.remove(os.path.join(directory, filename))
                            filename = record_id + '.' + img_type
                            image.save(os.path.join(directory, filename))
                        else:
                            flash('Недопустимый тип файла.', 'warning')
                except Exception as ex:
                    flash('Не удалось прикрепить изображение.', 'warning')
                    logging.error(ex)

                if send_in_telegram is not None:
                    send_news(record_text, filename)
                    flash('Вы отправили новость в телеграмм.', 'success')
            elif request.form['btn_news'] == 'send_telegram':
                record_id = request.form.get("record_id")
                record_text = request.form.get("input_text")
                resp_status, data = encrypt_id_with_no_digits(record_id)
                record_id = data
                filename = ''
                directory = directories['records']
                files = os.listdir(directory)
                for file in files:
                    if record_id == file.split('.')[0]:
                        filename = file
                        break
                send_news(record_text, filename)
                flash('Вы отправили новость в телеграмм.', 'success')
            elif request.form['btn_news'] == 'edit_record':
                record_id = request.form.get("record_id")
                record_text = request.form.get("input_text")
                lifetime = request.form.get("input_lifetime")
                if lifetime == 'Никогда':
                    lifetime = 0
                elif lifetime == 'День':
                    lifetime = 1
                elif lifetime == 'Неделя':
                    lifetime = 7
                else:
                    lifetime = int(lifetime)
                    if lifetime < 0 or lifetime > 365:
                        flash('Число дней может быть от 0 до 365.', 'warning')
                        return redirect(url_for('teacher.teacher_news'))

                update_record_news(record_id, record_text, lifetime)
                flash('Вы обновили новость.', 'success')

                # image
                try:
                    image = request.files['record_image']
                    img_type = image.filename.split('.')[-1].lower()
                    if img_type != '':
                        if img_type in valid_images:
                            resp_status, data = encrypt_id_with_no_digits(str(record_id))
                            record_id = data
                            filename = ''
                            directory = directories['records']
                            files = os.listdir(directory)
                            for file in files:
                                if record_id == file.split('.')[0]:
                                    filename = file
                                    break
                            if filename != '':
                                os.remove(os.path.join(directory, filename))
                            filename = record_id + '.' + img_type
                            image.save(os.path.join(directory, filename))
                        else:
                            flash('Недопустимый тип файла.', 'warning')
                except Exception as ex:
                    flash('Не удалось изменить изображение.', 'warning')
                    logging.error(ex)

            elif request.form['btn_news'] == 'delete_record':
                rec_id = request.form.get("record_id")
                try:
                    resp_status, data = encrypt_id_with_no_digits(str(rec_id))
                    record_id = data
                    filename = ''
                    directory = directories['records']
                    files = os.listdir(directory)
                    for file in files:
                        if record_id == file.split('.')[0]:
                            filename = file
                            break
                    if filename != '':
                        os.remove(os.path.join(directory, filename))
                except Exception as ex:
                    logging.error(ex)

                delete_record(rec_id)
                flash('Вы удалили новость.', 'success')

        except Exception as ex:
            logging.error(ex)
            flash('Произошла какая-то ошибка', 'error')

    user_news = []
    recs = sorted(get_records_by_author(current_user.id).data, key=lambda rec: rec.time, reverse=True)
    for rec in recs:
        if rec.type == RecordType.NEWS:
            record_status, record_id = encrypt_id_with_no_digits(str(rec.id))
            if record_status:
                user_news.append({
                    'id': f'{record_id}',
                    'record_id': str(rec.id),
                    'text': rec.text,
                    'lifetime': "Никогда" if rec.lifetime == 0 else rec.lifetime,
                    'time': rec.time.strftime("%d.%m.%Y %H:%M:%S")
                })
    return render_template("teacher/news.html", news=user_news)


# Уровень:              account
# База данных:          User
# HTML:                 account
@teacher.route('/account', methods=['POST', 'GET'])
@login_required
def teacher_account():
    # auto redirect
    status, url = auto_redirect(ignore_role=Role.TEACHER)
    if status:
        return redirect(url)
    # check session
    if not check_session():
        logout_user()
        return redirect(url_for("view.landing"))
    if request.method == "POST":
        avatar = request.files['avatar']
        img_type = avatar.filename.split('.')[-1].lower()
        if img_type in valid_images:
            try:
                resp_status, data = encrypt_id_with_no_digits(str(current_user.id))
                if not resp_status:
                    flash('Не удалось обработать данные.', category='error')
                    return redirect(url_for('teacher.teacher_account'))
                else:
                    user_id = data
                    filename = ''
                    directory = directories['avatars']
                    files = os.listdir(directory)
                    for file in files:
                        if user_id == file.split('.')[0]:
                            filename = file
                            break
                    if filename != '':
                        os.remove(os.path.join(directory, filename))
                    avatar.save(os.path.join(directory, user_id + '.' + img_type))
            except Exception as ex:
                logging.error(ex)
            flash('Аватарка успешно обновлена', category='success')
            return redirect(url_for('teacher.teacher_account'))
        else:
            flash('Такое расширение файла не подходит', category='warning')
    return render_template("teacher/account.html", friends=get_friends(str(current_user.id)),
                           courses=get_courses_by_teacher(current_user.id).data)


# Уровень:              courses/schedule
# База данных:          User
# HTML:                 schedule
@teacher.route('/courses/schedule', methods=['POST', 'GET'])
@login_required
def teacher_schedule():
    # auto redirect
    status, url = auto_redirect(ignore_role=Role.TEACHER)
    if status:
        return redirect(url)
    # check session
    if not check_session():
        logout_user()
        return redirect(url_for("view.landing"))
    return render_template("teacher/courses/schedule.html", courses=get_courses_by_teacher(current_user.id).data)


# Уровень:              attendance_markers
# База данных:          -
# HTML:                 attendance-markers
@teacher.route('/attendance_markers', methods=['POST', 'GET'])
@login_required
def teacher_attendance_markers():
    # auto redirect
    status, url = auto_redirect(ignore_role=Role.TEACHER)
    if status:
        return redirect(url)
    # check session
    if not check_session():
        logout_user()
        return redirect(url_for("view.landing"))

    if request.method == "POST":
        try:
            if request.form['btn_markers'] == 'add_marker':
                name = request.form.get('name')
                date_range = request.form.get('date_range').split(' - ')
                add_attendance_marker(name,
                                      datetime.strptime(date_range[0], "%d.%m.%Y %H:%M:%S"),
                                      datetime.strptime(date_range[1], "%d.%m.%Y %H:%M:%S"))
                flash('Вы успешно добавили посещаемость по ссылке', 'success')
        except Exception as ex:
            logging.error(ex)

    return render_template("teacher/courses/attendance-markers.html", attendance_markers=get_attendance_markers().data)


# Уровень:              attendance_markers
# База данных:          -
# HTML:                 attendance-marker
@teacher.route('/attendance_markers/<marker_id>', methods=['POST', 'GET'])
@login_required
def teacher_attendance_marker(marker_id):
    # auto redirect
    status, url = auto_redirect(ignore_role=Role.TEACHER)
    if status:
        return redirect(url)
    # check session
    if not check_session():
        logout_user()
        return redirect(url_for("view.landing"))

    if request.method == "POST":
        try:
            if request.form['btn_marker'] == 'save_marker':
                name = request.form.get('name')
                date_range = request.form.get('date_range').split(' - ')
                update_attendance_marker(marker_id,
                                         name,
                                         datetime.strptime(date_range[0], "%d.%m.%Y %H:%M:%S"),
                                         datetime.strptime(date_range[1], "%d.%m.%Y %H:%M:%S"))
                flash('Вы успешно обновили посещаемость по ссылке', 'success')
            elif request.form['btn_marker'] == 'delete_marker':
                delete_attendance_marker(marker_id)
                flash('Вы успешно удалили посещаемость по ссылке', 'success')
            elif request.form['btn_marker'] == 'commit_marker':
                checked_students = request.form.getlist('checked_students')
                date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                for student_id in checked_students:
                    add_attendance(student_id, 1, date)
                delete_attendance_marker(marker_id)
                flash('Вы успешно проставили посещаемость и удалили ссылку', 'success')
                return redirect(url_for('teacher.teacher_attendance_markers'))
        except Exception as ex:
            logging.error(ex)

    r = get_attendance_marker_by_id(marker_id)
    if not r.success:
        return redirect(url_for('teacher.teacher_attendance_markers'))
    marker = r.data

    students = []
    for student_id in marker.students:
        r = get_user_by_id(student_id)
        if r.success:
            student = r.data
            # str необходим для избежания исключений с None
            students.append({
                "check": f'<div class="form-check"><input type="checkbox" class="form-check-input dt-checkboxes" name="checked_students" value="{student_id}" checked><label class="form-check-label"></label></div>',
                "id": f'<a href="{url_for("networking.profile", user_id=student_id)}" target="_blank">{student_id}</a>',
                "first_name": student.first_name,
                "last_name": student.last_name
            })

    return render_template("teacher/courses/attendance-marker.html", students=students, marker=marker)


# Уровень:              attendance
# База данных:          -
# HTML:                 attendance
@teacher.route('/attendance', methods=['POST', 'GET'])
@login_required
def teacher_attendance():
    # auto redirect
    status, url = auto_redirect(ignore_role=Role.TEACHER)
    if status:
        return redirect(url)
    # check session
    if not check_session():
        logout_user()
        return redirect(url_for("view.landing"))

    if request.method == "POST":
        try:
            if 'add_attendance' in [request.values[i] for i in request.values]:
                selected_students = request.form.getlist('students_attendance')
                date = request.form.get('date_attendance')
                for student in selected_students:
                    add_attendance(student, 1, f'{date} 00:00:00')
                flash('Вы успешно добавили посещаемость', 'success')
                return redirect(url_for('teacher.teacher_attendance'))
            else:
                reward = request.form['reward']
                start = int(request.form['start'])
                end = int(request.form['end'])
                rewards = []
                if len(reward) == 0:
                    rewards = [Reward.TRIP, Reward.GRANT, Reward.NULL]
                else:
                    for i in reward.split(';'):
                        if len(i) > 0:
                            rewards.append(Reward(i))

                users = list()
                users_with_bad_attendance = list()
                now = datetime.now()
                trip_date = datetime.strptime(system_variables['yahad_trip'], "%d.%m.%Y")
                days_remaining = (trip_date - now).days
                weeks_remaining = int(days_remaining / 7)

                months = {
                    9: 'september',
                    10: 'october',
                    11: 'november',
                    12: 'december',
                    1: 'january',
                    2: 'february',
                    3: 'march',
                    4: 'april',
                    5: 'may',
                    6: 'june'
                }

                for user in get_users().data:
                    try:
                        if user.role == Role.STUDENT and user.reward in rewards:
                            d = {
                                "name": f'<a href=\"{url_for("teacher.teacher_user_attendance", user_id=str(user.id))}\" target="_blank">{rus2eng(user.last_name)} {rus2eng(user.first_name)}</a>',
                                "september": 0,
                                "october": 0,
                                "november": 0,
                                "december": 0,
                                "january": 0,
                                "february": 0,
                                "march": 0,
                                "april": 0,
                                "may": 0,
                                "june": 0,
                                "all": 0
                            }
                            for i in get_attendances_by_user_id(user.id).data:
                                date = i.date
                                if (date.year == start and date.month >= 9) or (
                                        date.year == end and date.month < 9):
                                    if date.month in months.keys():
                                        d[months[date.month]] += i.count
                                        d['all'] += i.count

                            users.append(d)
                            if user.reward == Reward.TRIP:
                                if now < trip_date:
                                    visits_count = d['all']
                                    if visits_count + weeks_remaining < 25:
                                        users_with_bad_attendance.append({
                                            "name": f'<a href=\"{url_for("teacher.user_attendance", user_id=str(user.id))}\" target="_blank">{user.first_name} {user.last_name}</a>',
                                            "visits": visits_count
                                        })
                    except Exception as ex:
                        logging.error(ex)
                return json.dumps({'success': True, 'users': users,
                                   'users_with_bad_attendance': users_with_bad_attendance}), 200, {
                    'ContentType': 'application/json'}
        except Exception as ex:
            logging.error(f'get_attendance: {ex}')
        return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}

    students = []
    for student in get_users_by_role(Role.STUDENT).data:
        if student.reward != Reward.NULL:
            students.append({"name": f'{student.first_name} {student.last_name}', "id": str(student.id)})

    return render_template("teacher/courses/attendance.html", students=students)


# Уровень:              attendance/user_id
# База данных:          User, attendance
# HTML:                 user-attendance
@teacher.route('/attendance/<user_id>', methods=['POST', 'GET'])
@login_required
def teacher_user_attendance(user_id):
    # auto redirect
    status, url = auto_redirect(ignore_role=Role.TEACHER)
    if status:
        return redirect(url)
    # check session
    if not check_session():
        logout_user()
        return redirect(url_for("view.landing"))

    if request.method == "POST":
        try:
            if request.form['btn_user_attendance'] == 'add_attendance':
                attendance_date = request.form.get('attendance_date')
                attendance_count = request.form.get('attendance_count')
                if not (1 <= int(attendance_count) <= 10):
                    flash('Число посещений должно быть от 1 до 10', 'error')
                elif not re.fullmatch(r'\d\d.\d\d.\d\d\d\d \d\d:\d\d:\d\d', attendance_date):
                    flash('Дата посещения должна иметь формат ДД.ММ.ГГГГ ЧЧ:ММ:СС', 'error')
                else:
                    add_attendance(user_id=user_id, date=attendance_date, count=attendance_count)
                    flash('Вы успешно добавили данные', 'success')
            elif request.form['btn_user_attendance'] == 'delete_attendance':
                attendance_id = request.form.get('attendance_id')
                delete_attendance(attendance_id)
                flash('Вы успешно удалили данные', 'success')
            elif request.form['btn_user_attendance'] == 'edit_attendance':
                attendance_id = request.form.get('attendance_id')
                attendance_date = request.form.get('attendance_date')
                attendance_count = request.form.get('attendance_count')
                if not (1 <= int(attendance_count) <= 10):
                    flash('Число посещений должно быть от 1 до 10', 'error')
                elif not re.fullmatch(r'\d\d.\d\d.\d\d\d\d \d\d:\d\d:\d\d', attendance_date):
                    flash('Дата посещения должна иметь формат ДД.ММ.ГГГГ ЧЧ:ММ:СС', 'error')
                else:
                    update_attendance(id=attendance_id, date=attendance_date, count=attendance_count)
                    flash('Вы успешно обновили данные', 'success')
            elif request.form['btn_user_attendance'] == 'get_attendance':
                try:
                    start = request.form['start']
                    end = request.form['end']

                    d = {
                        "september": [],
                        "october": [],
                        "november": [],
                        "december": [],
                        "january": [],
                        "february": [],
                        "march": [],
                        "april": [],
                        "may": [],
                        "june": []
                    }

                    months = {
                        9: 'september',
                        10: 'october',
                        11: 'november',
                        12: 'december',
                        1: 'january',
                        2: 'february',
                        3: 'march',
                        4: 'april',
                        5: 'may',
                        6: 'june'
                    }

                    for i in get_attendances_by_user_id(user_id).data:
                        date = i.date
                        if (str(date.year) == start and date.month >= 9) or (str(date.year) == end and date.month < 9):
                            if date.month in months.keys():
                                d[months[date.month]].append(
                                    {"id": str(i.id), "date": date.strftime("%d.%m.%Y %H:%M:%S"), "count": i.count})

                    return json.dumps({'success': True, 'data': d}), 200, {
                        'ContentType': 'application/json'}
                except Exception as ex:
                    logging.error(f'get_user_attendance: {ex}')
                return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}
        except Exception as ex:
            logging.error(ex)
            flash('Произошла какая-то ошибка', 'error')

    try:
        resp = get_user_by_id(user_id)
        if not resp.success:
            return render_template("error-500.html")
    except Exception as ex:
        logging.error(ex)
        return render_template("error-500.html")

    user_data = resp.data
    #if user_data.reward == Reward.NULL:
    #    return redirect(url_for("teacher.teacher_home"))

    return render_template("teacher/courses/user-attendance.html", user=user_data)
