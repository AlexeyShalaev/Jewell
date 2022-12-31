import os
from flask import *
from flask_login import *
from flask_toastr import *
from ManagementSystem.ext import trip_date
from ManagementSystem.ext.crypt import *
from ManagementSystem.ext.database.records import get_records_by_type, RecordType
from ManagementSystem.ext.database.maps import get_map_by_name
from ManagementSystem.ext.database.attendances import *
from ManagementSystem.ext.database.offers import *
from ManagementSystem.ext.logistics import *
from ManagementSystem.ext.tools import *

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
    trip_map = {"values": {}, "colors": {}}
    resp = get_map_by_name(name='trips')
    if resp.success:
        countries = resp.data.countries
        for i in range(len(countries)):
            trip_map["values"][countries[i]] = i + 1
            trip_map["colors"][str(i + 1)] = get_random_color()
    return render_template("student/home.html", shabbat=shabbat(), news=set_records(get_records_by_type(RecordType.NEWS)),
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
        return render_template("student/courses/no-reward.html")
    return render_template("student/courses/attendance.html", visits_count=visits_count, visits_aim=visits_aim,
                           progress_color=progress_color, percent=percent, frequency=frequency,
                           extra_info=extra_info,
                           visits_dataset=visits_dataset)


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
        return render_template("student/navigator/no-offers.html")
    if request.method == "POST":
        # TODO сделать логику запросов
        pass
    # TODO сделать страницу
    return render_template("student/navigator/offers.html", offers=offers.data)


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
    return render_template("student/navigator/mezuzah.html")
