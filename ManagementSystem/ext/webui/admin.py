import os
import re
from datetime import datetime
from logging import getLogger

from flask import *
from flask_login import *
from flask_toastr import *

from ManagementSystem.ext.database.attendances import delete_attendance, add_attendance, update_attendance
from ManagementSystem.ext.crypt import encrypt_id_with_no_digits
from ManagementSystem.ext.database.users import get_users_by_role, get_user_by_id
from ManagementSystem.ext.database.courses import get_courses, add_course, delete_course, update_course, \
    check_course_by_name
from ManagementSystem.ext.database.maps import get_map_by_name, update_trips
from ManagementSystem.ext.database.records import get_records_by_author, get_records_by_type, RecordType, add_record, \
    update_record_news, delete_record
from ManagementSystem.ext.logistics import auto_redirect, check_session
from ManagementSystem.ext.models.userModel import Role
from ManagementSystem.ext.telegram_bot.message import send_news
from ManagementSystem.ext.tools import shabbat, get_random_color, set_records, get_friends

logger = getLogger(__name__)  # logging
admin = Blueprint('admin', __name__, url_prefix='/admin', template_folder='templates/admin')


# Уровень:              Главная страница
# База данных:          User
# HTML:                 home
@admin.route('/')
@admin.route('/home', methods=['POST', 'GET'])
@login_required
def admin_home():
    # auto redirect
    status, url = auto_redirect(ignore_role=Role.ADMIN)
    if status:
        return redirect(url)
    # check session
    if not check_session():
        logout_user()
        return redirect(url_for("view.landing"))

    if request.method == "POST":
        try:
            if request.form['btn_home'] == 'upd_map':
                countries = request.form.getlist('countries')
                update_trips(countries)
                flash('Вы успешно обновили карту поездок', 'success')
        except Exception as ex:
            logger.error(ex)
            flash('Произошла какая-то ошибка', 'error')

    trip_map = {"values": {}, "colors": {}}
    resp = get_map_by_name(name='trips')
    if resp.success:
        countries = resp.data.countries
        for i in range(len(countries)):
            trip_map["values"][countries[i]] = i + 1
            trip_map["colors"][str(i + 1)] = get_random_color()
    return render_template("admin/home.html", shabbat=shabbat(),
                           news=set_records(get_records_by_type(RecordType.NEWS)),
                           map=trip_map)


# Уровень:              courses/schedule
# База данных:          User
# HTML:                 schedule
@admin.route('/news', methods=['POST', 'GET'])
@login_required
def admin_news():
    # auto redirect
    status, url = auto_redirect(ignore_role=Role.ADMIN)
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
                        return redirect(url_for('admin.admin_news'))

                inserted_record = add_record(current_user.id, record_text, datetime.now(), type=RecordType.NEWS,
                                             lifetime=lifetime)
                flash('Вы добавили новость.', 'success')

                # image
                filename = ''
                try:
                    image = request.files['record_image']
                    img_type = image.filename.split('.')[-1].lower()
                    if img_type != '':
                        types = ['jpeg', 'jpg', 'png']
                        if img_type in types:
                            resp_status, data = encrypt_id_with_no_digits(str(inserted_record.inserted_id))
                            record_id = data
                            directory = 'storage/records/'
                            files = os.listdir(directory)
                            for file in files:
                                if record_id == file.split('.')[0]:
                                    filename = file
                                    break
                            if filename != '':
                                os.remove(directory + filename)
                            filename = record_id + '.' + img_type
                            image.save(directory + filename)
                        else:
                            flash('Недопустимый тип файла.', 'warning')
                except Exception as ex:
                    flash('Не удалось прикрепить изображение.', 'warning')
                    logger.error(ex)

                if send_in_telegram is not None:
                    send_news(record_text, filename)
                    flash('Вы отправили новость в телеграмм.', 'success')
            elif request.form['btn_news'] == 'send_telegram':
                record_id = request.form.get("record_id")
                record_text = request.form.get("input_text")
                resp_status, data = encrypt_id_with_no_digits(record_id)
                record_id = data
                filename = ''
                directory = 'storage/records/'
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
                        return redirect(url_for('admin.admin_news'))

                update_record_news(record_id, record_text, lifetime)
                flash('Вы обновили новость.', 'success')

                # image
                try:
                    image = request.files['record_image']
                    img_type = image.filename.split('.')[-1].lower()
                    if img_type != '':
                        types = ['jpeg', 'jpg', 'png']
                        if img_type in types:
                            resp_status, data = encrypt_id_with_no_digits(str(record_id))
                            record_id = data
                            filename = ''
                            directory = 'storage/records/'
                            files = os.listdir(directory)
                            for file in files:
                                if record_id == file.split('.')[0]:
                                    filename = file
                                    break
                            if filename != '':
                                os.remove(directory + filename)
                            filename = record_id + '.' + img_type
                            image.save(directory + filename)
                        else:
                            flash('Недопустимый тип файла.', 'warning')
                except Exception as ex:
                    flash('Не удалось изменить изображение.', 'warning')
                    logger.error(ex)

            elif request.form['btn_news'] == 'delete_record':
                rec_id = request.form.get("record_id")
                try:
                    resp_status, data = encrypt_id_with_no_digits(str(rec_id))
                    record_id = data
                    filename = ''
                    directory = 'storage/records/'
                    files = os.listdir(directory)
                    for file in files:
                        if record_id == file.split('.')[0]:
                            filename = file
                            break
                    if filename != '':
                        os.remove(directory + filename)
                except Exception as ex:
                    logger.error(ex)

                delete_record(rec_id)
                flash('Вы удалили новость.', 'success')

        except Exception as ex:
            logger.error(ex)
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
    return render_template("admin/news.html", news=user_news)


# Уровень:              account
# База данных:          User
# HTML:                 account
@admin.route('/account', methods=['POST', 'GET'])
@login_required
def admin_account():
    # auto redirect
    status, url = auto_redirect(ignore_role=Role.ADMIN)
    if status:
        return redirect(url)
    # check session
    if not check_session():
        logout_user()
        return redirect(url_for("view.landing"))
    if request.method == "POST":
        avatar = request.files['avatar']
        img_type = avatar.filename.split('.')[-1].lower()
        types = ['jpeg', 'jpg', 'png']
        if img_type in types:
            try:
                resp_status, data = encrypt_id_with_no_digits(str(current_user.id))
                if not resp_status:
                    flash('Не удалось обработать данные.', category='error')
                    return redirect(url_for('admin.admin_account'))
                else:
                    user_id = data
                    filename = ''
                    directory = 'storage/avatars/'
                    files = os.listdir(directory)
                    for file in files:
                        if user_id == file.split('.')[0]:
                            filename = file
                            break
                    if filename != '':
                        os.remove(directory + filename)
                    avatar.save(directory + user_id + '.' + img_type)
            except Exception as ex:
                logger.error(ex)
            flash('Аватарка успешно обновлена', category='success')
            return redirect(url_for('admin.admin_account'))
        else:
            flash('Такое расширение файла не подходит', category='warning')
    return render_template("admin/account.html", friends=get_friends(str(current_user.id)))


# Уровень:              courses/schedule
# База данных:          User
# HTML:                 schedule
@admin.route('/courses/schedule', methods=['POST', 'GET'])
@login_required
def admin_schedule():
    # auto redirect
    status, url = auto_redirect(ignore_role=Role.ADMIN)
    if status:
        return redirect(url)
    # check session
    if not check_session():
        logout_user()
        return redirect(url_for("view.landing"))

    if request.method == "POST":
        try:
            if request.form['btn_schedule'] == 'add_course':
                course_name = request.form.get('course_name')
                if check_course_by_name(course_name):
                    flash('Курс с таким именем уже существует', 'warning')
                else:
                    course_teachers = request.form.getlist('course_teachers')
                    course_times = request.form.getlist('course_times')
                    timetable = dict()
                    for time in course_times:
                        d, h, m = time.split('-')
                        timetable[d] = '{"hours": ' + h + ', "minutes": ' + m + '}'
                    add_course(teachers=course_teachers, name=course_name, timetable=timetable)
                    flash('Вы успешно добавили курс', 'success')
            elif request.form['btn_schedule'] == 'delete_course':
                course_id = request.form.get('course_id')
                delete_course(course_id)
                flash('Вы успешно удалили курс', 'success')
            elif request.form['btn_schedule'] == 'edit_course':
                course_id = request.form.get('course_id')
                course_name = request.form.get('course_name')
                course_teachers = request.form.getlist('course_teachers')
                course_times = request.form.getlist('course_times')
                timetable = dict()
                for time in course_times:
                    d, h, m = time.split('-')
                    timetable[d] = '{"hours": ' + h + ', "minutes": ' + m + '}'
                update_course(id=course_id, name=course_name, teachers=course_teachers, timetable=timetable)
                flash('Вы успешно обновили курс', 'success')
        except Exception as ex:
            logger.error(ex)
            flash('Произошла какая-то ошибка', 'error')

    teachers = []
    for teacher in get_users_by_role(Role.TEACHER).data:
        teachers.append({"name": f'{teacher.first_name} {teacher.last_name}', "id": str(teacher.id)})
    return render_template("admin/courses/schedule.html", courses=get_courses().data, teachers=teachers)


# Уровень:              attendance
# База данных:          -
# HTML:                 attendance
@admin.route('/attendance', methods=['POST', 'GET'])
@login_required
def admin_attendance():
    # auto redirect
    status, url = auto_redirect(ignore_role=Role.ADMIN)
    if status:
        return redirect(url)
    # check session
    if not check_session():
        logout_user()
        return redirect(url_for("view.landing"))
    return render_template("admin/courses/attendance.html")


# Уровень:              attendance/user_id
# База данных:          User, attendance
# HTML:                 user-attendance
@admin.route('/attendance/<user_id>', methods=['POST', 'GET'])
@login_required
def user_attendance(user_id):
    # auto redirect
    status, url = auto_redirect(ignore_role=Role.ADMIN)
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
        except Exception as ex:
            logger.error(ex)
            flash('Произошла какая-то ошибка', 'error')

    try:
        resp = get_user_by_id(user_id)
        if not resp.success:
            return render_template("error-500.html")
    except Exception as ex:
        logger.error(ex)
        return render_template("error-500.html")

    return render_template("admin/courses/user-attendance.html", user=resp.data)
