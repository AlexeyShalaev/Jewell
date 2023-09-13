import logging
import os
from datetime import datetime

from flask import *
from flask_login import *
from flask_toastr import *

from ManagementSystem.ext import system_variables, directories, valid_images
from ManagementSystem.ext.attendance_visits import handle_visit
from ManagementSystem.ext.crypt import encrypt_id_with_no_digits
from ManagementSystem.ext.database.attendances import get_attendances_by_user_id, get_attendance_marker_by_id, \
    join_attendance_marker
from ManagementSystem.ext.database.maps import get_map_by_name
from ManagementSystem.ext.database.qr_codes import check_qr_code_by_id, get_qr_code_by_name
from ManagementSystem.ext.database.records import get_records_by_type, RecordType
from ManagementSystem.ext.logistics import auto_redirect, check_session
from ManagementSystem.ext.models.userModel import Role, Reward, Sex
from ManagementSystem.ext.models.visit import VisitType
from ManagementSystem.ext.tools import shabbat, get_random_color, set_records, get_friends, get_month

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
    trip_map = {"values": {}, "colors": {}}
    resp = get_map_by_name(name='trips')
    if resp.success:
        countries = resp.data.countries
        for i in range(len(countries)):
            trip_map["values"][countries[i]] = i + 1
            trip_map["colors"][str(i + 1)] = get_random_color()
    return render_template("student/home.html", shabbat=shabbat(),
                           news=set_records(get_records_by_type(RecordType.NEWS)),
                           map=trip_map)


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
        img_type = avatar.filename.split('.')[-1].lower()
        if img_type in valid_images:
            try:
                resp_status, data = encrypt_id_with_no_digits(str(current_user.id))
                if not resp_status:
                    flash('Не удалось обработать данные.', category='error')
                    return redirect(url_for('student.student_account'))
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
            return redirect(url_for('student.student_account'))
        else:
            flash('Такое расширение файла не подходит', category='warning')
    return render_template("student/account.html", friends=get_friends(str(current_user.id)))


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

    resp = get_attendances_by_user_id(current_user.id)
    if not resp.success:
        return render_template("error-500.html")
    now = datetime.now()
    current_year = now.year
    if now.month >= 9:
        start = current_year
        end = current_year + 1
    else:
        start = current_year - 1
        end = current_year

    if request.method == "POST":
        start = int(request.form['start'])
        end = int(request.form['end'])

    attendance = []
    for i in resp.data:
        date = i.date
        if (date.year == start and date.month >= 9) or (date.year == end and date.month < 9):
            attendance.append(i)

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
        trip_date = datetime.strptime(system_variables['yahad_trip'], "%d.%m.%Y")
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
    return render_template("student/courses/attendance.html", visits_count=visits_count, visits_aim=visits_aim,
                           progress_color=progress_color, percent=percent, frequency=frequency,
                           extra_info=extra_info,
                           visits_dataset=visits_dataset, attendance=attendance)


# Уровень:              attendance
# База данных:          User
# HTML:                 attendance
@student.route('/attendance_markers/<marker_id>', methods=['POST', 'GET'])
@login_required
def student_attendance_marker(marker_id):
    # auto redirect
    status, url = auto_redirect(ignore_role=Role.STUDENT)
    if status:
        return redirect(url)
    # check session
    if not check_session():
        logout_user()
        return redirect(url_for("view.landing"))

    r = get_attendance_marker_by_id(marker_id)
    if not r.success:
        return redirect(url_for('student.student_home'))
    marker = r.data

    now = datetime.now()

    if now < marker.start or now > marker.finish:
        flash('Данная страница не доступна', 'info')
        return redirect(url_for('student.student_home'))

    if current_user.id in marker.students:
        flash('Данную ссылку можно использовать только один раз', 'info')
        return redirect(url_for('student.student_home'))

    if current_user.reward == Reward.NULL:
        flash('У вас нет награды, обратитесь к администрации', 'warning')
        return redirect(url_for('student.student_home'))

    if request.method == "POST":
        try:
            if request.form['btn_marker'] == 'join_marker':
                join_attendance_marker(marker_id, current_user.id)
                flash('Вы добавлены в список участников, ожидайте подтверждения вашего участия', 'success')
                return redirect(url_for('admin.admin_attendance_markers'))
        except Exception as ex:
            logging.error(ex)

    return render_template("student/courses/attendance-marker.html", marker=marker)


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
    return render_template("student/courses/schedule.html")


# Уровень:              attendance
# База данных:          User
# HTML:                 attendance
@student.route('/attendance_qr/<qr_token>', methods=['POST', 'GET'])
@login_required
def student_attendance_qr(qr_token):
    # auto redirect
    status, url = auto_redirect(ignore_role=Role.STUDENT)
    if status:
        return redirect(url)
    # check session
    if not check_session():
        logout_user()
        return redirect(url_for("view.landing"))

    qr_code_name = 'jewell_mirror_visits'
    r = get_qr_code_by_name(qr_code_name)

    if not r.success:
        flash('Произошла какая-то ошибка :)', 'error')
        return redirect(url_for('student.student_home'))

    if r.data.uri.split('/')[-1] != qr_token:
        flash('Данной страницы не существует :)', 'error')
        return redirect(url_for('student.student_home'))

    for i in handle_visit(current_user, datetime.now()):
        if i['visit_type'] == VisitType.ENTER.value:
            flash(
                f"{current_user.first_name} {'пришла' if current_user.sex == Sex.FEMALE else 'пришел'} на занятие {'/'.join(i['courses'])}",
                'success')
        elif i['visit_type'] == VisitType.EXIT.value:
            flash(
                f"{current_user.first_name} {'ушла' if current_user.sex == Sex.FEMALE else 'ушел'} на занятие {'/'.join(i['courses'])}",
                'success')

    return redirect(url_for('student.student_home'))
