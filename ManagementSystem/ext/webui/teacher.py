import os
from flask import *
from flask_login import *
from flask_toastr import *
from ManagementSystem.ext.database.records import get_records_by_type, RecordType
from ManagementSystem.ext.database.maps import get_map_by_name
from ManagementSystem.ext.database.offers import *
from ManagementSystem.ext.database.courses import get_courses_by_teacher
from ManagementSystem.ext.logistics import *
from ManagementSystem.ext.tools import *

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

    return render_template("teacher/news.html")


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
        img_type = avatar.filename.split('.')[-1]
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


# Уровень:              offers
# База данных:          Offers
# HTML:                 offers
@teacher.route('/offers', methods=['POST', 'GET'])
@login_required
def teacher_offers():
    # auto redirect
    status, url = auto_redirect(ignore_role=Role.TEACHER)
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
        return render_template("teacher/navigator/no-offers.html")
    if request.method == "POST":
        # TODO сделать логику запросов
        pass
    # TODO сделать страницу
    return render_template("teacher/navigator/offers.html", offers=offers.data)


# Уровень:              mezuzah
# База данных:          TODO: products
# HTML:                 mezuzah
@teacher.route('/mezuzah', methods=['POST', 'GET'])
@login_required
def teacher_mezuzah():
    # auto redirect
    status, url = auto_redirect(ignore_role=Role.TEACHER)
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
    return render_template("teacher/navigator/mezuzah.html")
