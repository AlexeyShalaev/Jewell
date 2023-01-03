import logging
import os
from datetime import datetime

from flask import *
from flask_login import *
from flask_toastr import *

from ManagementSystem.ext.crypt import encrypt_id_with_no_digits
from ManagementSystem.ext.database.courses import get_courses_by_teacher
from ManagementSystem.ext.database.maps import get_map_by_name
from ManagementSystem.ext.database.records import get_records_by_author, get_records_by_type, RecordType, add_record, \
    update_record_news, delete_record
from ManagementSystem.ext.logistics import auto_redirect, check_session
from ManagementSystem.ext.models.userModel import Role
from ManagementSystem.ext.telegram_bot.message import send_news
from ManagementSystem.ext.tools import shabbat, get_random_color, set_records, get_friends

logger = logging.getLogger(__name__)  # logging
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


# Уровень:              courses/schedule
# База данных:          User
# HTML:                 schedule
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
                        return redirect(url_for('teacher.teacher_news'))

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
        types = ['jpeg', 'jpg', 'png']
        if img_type in types:
            try:
                resp_status, data = encrypt_id_with_no_digits(str(current_user.id))
                if not resp_status:
                    flash('Не удалось обработать данные.', category='error')
                    return redirect(url_for('teacher.teacher_account'))
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
