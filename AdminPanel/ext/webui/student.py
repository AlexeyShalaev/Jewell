import os
from AdminPanel.ext.tools import *
from AdminPanel.ext.logistics import *
from AdminPanel.ext.database.users import *
from AdminPanel.ext.database.offers import *
from AdminPanel.ext.database.records import *
from AdminPanel.ext.database.courses import *
from AdminPanel.ext.database.attendances import *
from AdminPanel.ext.database.flask_sessions import *
from flask import *
from flask_toastr import *
from flask_login import *
from AdminPanel.ext.crypt import *
from AdminPanel.ext import trip_date
from AdminPanel.ext.text_filter import TextFilter
import logging

logger = logging.getLogger(__name__)  # logging
student = Blueprint('student', __name__, url_prefix='/student', template_folder='templates/student',
                    static_folder='assets')


# Уровень:              Главная страница
# База данных:          User
# HTML:                 home
@student.route('/')
@student.route('/home', methods=['POST', 'GET'])
@login_required
def student_home():
    # auto redirect
    status, url = auto_redirect(ignore_role=Role.STUDENT)
    if status:
        return redirect(url)
    # check session
    if not check_session():
        logout_user()
        return redirect(url_for("view.landing"))
    # TODO сделать домашнюю страницу
    return render_template("home.html")


# Уровень:              account
# База данных:          User
# HTML:                 account
@student.route('/account', methods=['POST', 'GET'])
@login_required
def student_account():
    # auto redirect
    status, url = auto_redirect(ignore_role=Role.STUDENT)
    if status:
        return redirect(url)
    # check session
    if not check_session():
        logout_user()
        return redirect(url_for("view.landing"))
    if request.method == "POST":
        avatar = request.files['avatar']
        img_type = avatar.filename.split('.')[-1]
        types = ['jpeg', 'jpg', 'png']
        if img_type in types:
            try:
                resp_status, data = encrypt_id_with_no_digits(str(current_user.id))
                if not resp_status:
                    flash('Не удалось обработать данные.', category='error')
                    return redirect(url_for('student.student_account'))
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
            return redirect(url_for('student.student_account'))
        else:
            flash('Такое расширение файла не подходит', category='warning')
    return render_template("account.html")


# Уровень:              account/password
# База данных:          User
# HTML:                 -
@student.route('account/password', methods=['POST'])
def change_password():
    try:
        old_password = request.form["old"]
        new_password = request.form["new"]
        repeat_password = request.form["repeat"]
        if len(new_password) < 4:
            return json.dumps({'icon': 'warning', 'title': 'Смена пароля',
                               'text': 'Длина пароля должна быть больше 4.',
                               }), 200, {
                       'ContentType': 'application/json'}
        if new_password != repeat_password:
            return json.dumps({'icon': 'warning', 'title': 'Смена пароля',
                               'text': 'Пароли не совпадают.',
                               }), 200, {
                       'ContentType': 'application/json'}
        if new_password == old_password:
            return json.dumps({'icon': 'warning', 'title': 'Смена пароля',
                               'text': 'Новый пароль не отличается от старого.',
                               }), 200, {
                       'ContentType': 'application/json'}
        if not check_password_hash(current_user.password, old_password):
            return json.dumps({'icon': 'warning', 'title': 'Смена пароля',
                               'text': 'Вы ввели неверный старый пароль.',
                               }), 200, {
                       'ContentType': 'application/json'}
        crypt_status, crypted_pass = crypt_pass(new_password)
        if not crypt_status:
            return json.dumps({'icon': 'warning', 'title': 'Смена пароля',
                               'text': 'Не удалось зарегистрировать вас, возможно вы вводите недопустимый пароль.',
                               }), 200, {
                       'ContentType': 'application/json'}
        update_user(current_user.id, 'password', crypted_pass)
        return json.dumps({'icon': 'success', 'title': 'Смена пароля',
                           'text': 'Вы успешно сменили пароль.',
                           }), 200, {
                   'ContentType': 'application/json'}
    except Exception as ex:
        logger.error(ex)
        return json.dumps({'icon': 'error', 'title': 'Ошибка',
                           'text': str(ex)
                           }), 200, {'ContentType': 'application/json'}


# Уровень:              account/telegram
# База данных:          User
# HTML:                 -
@student.route('account/telegram', methods=['POST'])
def get_telegram_token():
    try:
        if current_user.telegram_id is None:
            status, token = create_token()
            if status:
                update_user(current_user.id, 'access_token', token)
                return json.dumps({'success': True, 'token': token}), 200, {'ContentType': 'application/json'}
    except Exception as ex:
        logger.error(ex)
    return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}


# Уровень:              account/telegram/auth
# База данных:          User
# HTML:                 -
@student.route('account/telegram/auth', methods=['POST'])
def set_telegram_auth():
    try:
        if current_user.telegram_id is not None:
            status = request.form['status'] == "true"
            update_user(current_user.id, 'telegram_auth', status)
            return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    except Exception as ex:
        logger.error(ex)
    return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}


# Уровень:              attendance
# База данных:          User
# HTML:                 attendance
@student.route('/attendance', methods=['POST', 'GET'])
@login_required
def student_attendance():
    # auto redirect
    status, url = auto_redirect(ignore_role=Role.STUDENT)
    if status:
        return redirect(url)
    # check session
    if not check_session():
        logout_user()
        return redirect(url_for("view.landing"))
    if request.method == "POST":
        # TODO сделать логику запросов
        pass
    resp = get_attendances_by_user_id(current_user.id)
    if not resp.success:
        return render_template("error-500.html")
    attendance = resp.data
    visits_count = len(attendance)
    # base set up
    now = datetime.now()
    visits_aim = '∞'
    percent = 0
    progress_color = 'bg-dark'
    frequency = '∞'
    extra_info = f'Ваша награда: {current_user.reward.value}'
    visits_dataset = []
    # TRIP set up
    if current_user.reward == Reward.TRIP:
        visits_aim = 30
        percent = int(visits_count / visits_aim * 100)
        if percent < 25:
            progress_color = 'bg-danger'
        elif percent < 50:
            progress_color = 'bg-warning'
        elif percent < 75:
            progress_color = 'bg-info'
        else:
            progress_color = 'bg-success'
        frequency_data_set = dict()
        for visit in attendance:
            key = f'{visit.date.month} {visit.date.year}'
            if key in frequency_data_set.keys():
                frequency_data_set[key] += 1 / 4
            else:
                frequency_data_set[key] = 1 / 4
        frequency_array = frequency_data_set.values()
        if len(frequency_array) == 0:
            frequency = 0
        else:
            frequency = int(sum(frequency_array) / len(frequency_array) * 1000) / 1000
        for k, v in frequency_data_set.items():
            m, y = map(int, k.split())
            visits_dataset.append({
                'x': f'{get_month(m)} {y}',
                'y': int(v * 4)
            })
        if now < trip_date:
            days_remaining = (trip_date - now).days
            weeks_remaining = int(days_remaining / 7)
            extra_info = f'До поездки осталось {days_remaining} дней. '
            if visits_count < 25:
                extra_info += f'Вам еще нужно минимум {25 - visits_count} посещений. '
                if visits_count + weeks_remaining < 25:
                    extra_info += f'Если вы будете ходить раз в неделю, то НЕ сможете выполнить план, поэтому ходите на отработки/доп занятия. '
                else:
                    extra_info += f'Если вы будете ходить раз в неделю, то сможете с легкостью выполнить план. '
            else:
                extra_info += f'Ваша посещаемость в норме. '
        else:
            if visits_count < 30:
                extra_info = f'Вам еще нужно минимум {30 - visits_count} посещений. '
            else:
                extra_info = f'Ваша посещаемость в норме. '
    # GRANT set up
    elif current_user.reward == Reward.GRANT:
        visits_count = 0
        visits_aim = 4
        frequency_data_set = dict()
        for visit in attendance:
            if visit.date.month == now.month:
                visits_count += 1
            key = f'{visit.date.month} {visit.date.year}'
            if key in frequency_data_set.keys():
                frequency_data_set[key] += 1 / 4
            else:
                frequency_data_set[key] = 1 / 4
        frequency_array = frequency_data_set.values()
        if len(frequency_array) == 0:
            frequency = 0
        else:
            frequency = int(sum(frequency_array) / len(frequency_array) * 1000) / 1000
        for k, v in frequency_data_set.items():
            m, y = map(int, k.split())
            visits_dataset.append({
                'x': f'{get_month(m)} {y}',
                'y': int(v * 4),
                'goals': [
                    {
                        'name': 'Планка',
                        'value': 8,
                        'strokeHeight': 5,
                        'strokeColor': '#775DD0'
                    }],
            })
        percent = int(visits_count / (visits_aim + 4) * 100)
        if percent < 50:
            progress_color = 'bg-danger'
        else:
            progress_color = 'bg-success'
        if visits_count < 4:
            extra_info = f'Вам необходимо посетить еще {visits_aim - visits_count} занятий для получения стипендии в размере: 65$'
        elif visits_count < 7:
            extra_info = f'Продолжайте ходить на занятия и увеличьте стипендию до {65 + 15 * (visits_count + 1 - 4)}$. На данный момент ваша стипендия составляет целых {65 + 15 * (visits_count - 4)}$'
        elif visits_count == 7:
            extra_info = f'Продолжайте ходить на занятия и увеличьте стипендию до 130$. На данный момент ваша стипендия составляет целых {65 + 15 * (visits_count - 4)}$'
        elif visits_count == 8:
            extra_info = f'Вы молодец! Ваша стипендия составляет целых 130$'
        else:
            extra_info = f'Мы очень гордимся вами. Ваша посещаемость идеальна :)'
    # No reward
    else:
        return render_template("no-reward.html")
    return render_template("attendance.html", visits_count=visits_count, visits_aim=visits_aim,
                           progress_color=progress_color, percent=percent, frequency=frequency,
                           extra_info=extra_info,
                           visits_dataset=visits_dataset)


# Уровень:              attendance/count
# База данных:          attendance
# HTML:                 -
@student.route('/attendance/count', methods=['POST'])
def attendance_count():
    try:
        cnt = len(get_attendances_by_user_id(current_user.id).data)
        if cnt > 0:
            return json.dumps({'data': cnt}), 200, {'ContentType': 'application/json'}
    except Exception as ex:
        logger.error(ex)
    return json.dumps({'data': ''}), 200, {'ContentType': 'application/json'}


# Уровень:              courses/schedule
# База данных:          User
# HTML:                 schedule
@student.route('/courses/schedule', methods=['POST', 'GET'])
@login_required
def student_schedule():
    # auto redirect
    status, url = auto_redirect(ignore_role=Role.STUDENT)
    if status:
        return redirect(url)
    # check session
    if not check_session():
        logout_user()
        return redirect(url_for("view.landing"))
    return render_template("schedule.html")


# Уровень:              courses/schedule/timetable
# База данных:          Courses
# HTML:                 -
@student.route('/courses/schedule/timetable', methods=['POST'])
def get_schedule():
    try:
        resp = get_courses()
        times = set()
        courses_names = set()
        if resp.success:
            courses = resp.data
            filtered_courses = []
            for course in courses:
                courses_names.add(course.name)
                teachers = []
                try:
                    for teacher in course.teachers:
                        r = get_user_by_id(teacher)
                        if r.success:
                            teachers.append(f'{r.data.first_name} {r.data.last_name}')
                except Exception:
                    pass
                filtered_courses.append({
                    "name": course.name,
                    "timetable": course.timetable,
                    "teachers": teachers
                })
                for k, v in course.timetable.items():
                    times.add(v.to_string())
            times = [Time.from_string(time) for time in times]
            times.sort()
            colors = dict()
            for name in courses_names:
                colors[name] = get_random_color()
            return json.dumps(
                {'success': True, 'times': times, 'courses': filtered_courses, 'colors': colors}), 200, {
                       'ContentType': 'application/json'}
    except Exception as ex:
        logger.error(ex)
    return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}


# Уровень:              offers
# База данных:          Offers
# HTML:                 offers
@student.route('/offers', methods=['POST', 'GET'])
@login_required
def student_offers():
    # auto redirect
    status, url = auto_redirect(ignore_role=Role.STUDENT)
    if status:
        return redirect(url)
    # check session
    if not check_session():
        logout_user()
        return redirect(url_for("view.landing"))
    if request.method == "POST":
        pass
    offers = get_offers()
    if len(offers.data) == 0:
        return render_template("no-offers.html")
    if request.method == "POST":
        # TODO сделать логику запросов
        pass
    # TODO сделать страницу
    return render_template("offers.html", offers=offers.data)


# Уровень:              offers/count
# База данных:          Offers
# HTML:                 -
@student.route('/offers/count', methods=['POST'])
def offers_count():
    try:
        cnt = len(get_offers().data)
        if cnt > 0:
            return json.dumps({'data': cnt}), 200, {'ContentType': 'application/json'}
    except Exception as ex:
        logger.error(ex)
    return json.dumps({'data': ''}), 200, {'ContentType': 'application/json'}


# Уровень:              mezuzah
# База данных:          TODO: products
# HTML:                 mezuzah
@student.route('/mezuzah', methods=['POST', 'GET'])
@login_required
def student_mezuzah():
    # auto redirect
    status, url = auto_redirect(ignore_role=Role.STUDENT)
    if status:
        return redirect(url)
    # check session
    if not check_session():
        logout_user()
        return redirect(url_for("view.landing"))
    if request.method == "POST":
        # TODO сделать логику запросов
        pass
    # TODO сделать страницу
    return render_template("mezuzah.html")


# NET WORKING


# Уровень:              networking/feed
# База данных:          User
# HTML:                 social-feed
@student.route('/networking/feed', methods=['POST', 'GET'])
@login_required
def student_feed():
    # auto redirect
    status, url = auto_redirect(ignore_role=Role.STUDENT)
    if status:
        return redirect(url)
    # check session
    if not check_session():
        logout_user()
        return redirect(url_for("view.landing"))
    if request.method == "POST":
        try:
            if request.form['btn_student_feed'] == 'add_record':
                record_text = request.form.get("record_text")
                # проверка на нецензурную лексику
                bad_words = TextFilter(record_text).find_bad_words()
                if len(bad_words) > 0:
                    flash(f'В вашем тексте были найдены недопустимые слова: {" ".join(bad_words)}')
                else:
                    add_record(current_user.id, record_text, datetime.now())
                    flash('Вы добавили запись.', 'success')
            elif request.form['btn_student_feed'] == 'edit_record':
                record_text = request.form.get("record_text")
                record_id = request.form.get("record_id")
                rec_status, rec_id = decrypt_id_with_no_digits(record_id)
                if not rec_status:
                    flash('Не удалось обработать данные.', 'error')
                else:
                    # проверка на нецензурную лексику
                    bad_words = TextFilter(record_text).find_bad_words()
                    if len(bad_words) > 0:
                        flash(f'В вашем тексте были найдены недопустимые слова: {" ".join(bad_words)}')
                    else:
                        update_record(rec_id, 'text', record_text)
                        flash('Вы добавили запись.', 'success')
            elif request.form['btn_student_feed'] == 'delete_record':
                record_id = request.form.get("record_id")
                rec_status, rec_id = decrypt_id_with_no_digits(record_id)
                if not rec_status:
                    flash('Не удалось обработать данные.', 'error')
                else:
                    delete_record(rec_id)
                    flash('Вы удалили запись.', 'success')
            elif request.form['btn_student_feed'] == 'profile':
                sex = request.form.get("editSex")
                location = request.form.get("editLocation")
                profession = request.form.get("editProfession")
                university = request.form.get("editUniversity")
                languages = request.form.getlist('editLanguages')
                tags = request.form.get("editTags").split()
                # проверка на нецензурную лексику
                bad_words = TextFilter(f'{location} {profession} {university} {tags}').find_bad_words()
                if len(bad_words) > 0:
                    flash(f'В ваших данных были найдены недопустимые слова: {" ".join(bad_words)}')
                else:
                    update_social_data(current_user.id, sex, location, profession, university, languages, tags)
                    flash('Вы успешно обновили данные', 'success')
            return redirect(url_for('student.student_feed'))
        except Exception as ex:
            logger.error(ex)
            flash('Произошла какая-то ошибка', 'error')
    records = []
    resp = get_records()
    if resp.success:
        recs = sorted(resp.data, key=lambda rec: rec.time, reverse=True)
        for rec in recs:
            r = get_user_by_id(rec.author)
            if r.success:
                author = r.data
                record_status, record_id = encrypt_id_with_no_digits(str(rec.id))
                if record_status:
                    records.append({
                        'record_id': f'{record_id}',
                        'user_id': f'{author.id}',
                        'author': f'{author.first_name} {author.last_name}',
                        'text': rec.text,
                        'time': rec.time.strftime("%m.%d.%Y %H:%M:%S")
                    })
    return render_template("social-feed.html", records=records)


# Уровень:              networking/profile
# База данных:          User
# HTML:                 profile
@student.route('/networking/profile/<user_id>', methods=['POST', 'GET'])
@login_required
def student_profile(user_id):
    # auto redirect
    status, url = auto_redirect(ignore_role=Role.STUDENT)
    if status:
        return redirect(url)
    # check session
    if not check_session():
        logout_user()
        return redirect(url_for("view.landing"))

    if str(current_user.id) == str(user_id):
        return redirect(url_for('student.student_feed'))

    resp = get_user_by_id(user_id)
    if not resp.success:
        flash('Не удалось найти пользователя.', category='error')
        return redirect(url_for('student.student_feed'))
    user = resp.data

    records = []
    resp = get_records_by_author(user_id)
    if resp.success:
        recs = sorted(resp.data, key=lambda rec: rec.time, reverse=True)
        for rec in recs:
            records.append({
                'author': f'{user.first_name} {user.last_name}',
                'text': rec.text,
                'time': rec.time.strftime("%m.%d.%Y %H:%M:%S")
            })
    return render_template("profile.html", records=records, user=user)
