import os
import re
from datetime import datetime
from logging import getLogger

from flask import *
from flask_login import *
from flask_toastr import *

from ManagementSystem.ext import trip_date
from ManagementSystem.ext.crypt import create_token
from ManagementSystem.ext.crypt import encrypt_id_with_no_digits
from ManagementSystem.ext.database.attendances import delete_attendance, add_attendance, update_attendance, \
    get_attendances_by_user_id
from ManagementSystem.ext.database.courses import get_courses, add_course, delete_course, update_course, \
    check_course_by_name, get_courses_by_teacher, update_course_teachers
from ManagementSystem.ext.database.flask_sessions import delete_flask_sessions_by_user_id, delete_flask_session, \
    add_flask_session, \
    get_flask_sessions
from ManagementSystem.ext.database.maps import get_map_by_name, update_trips
from ManagementSystem.ext.database.offers import get_offers, delete_offer, add_offer, delete_offers_by_user_id
from ManagementSystem.ext.database.orders import get_orders, delete_order, update_order, delete_orders_by_product_id, \
    delete_orders_by_user_id
from ManagementSystem.ext.database.products import get_products, get_product_by_id, add_product, update_product, \
    delete_product
from ManagementSystem.ext.database.records import get_records_by_author, get_records_by_type, RecordType, add_record, \
    update_record_news, delete_record, delete_records_by_user_id
from ManagementSystem.ext.database.recover_pw import get_recovers, delete_recover, delete_recovers_by_user_id
from ManagementSystem.ext.database.relationships import get_relationships_by_sender, delete_relationship, \
    get_relationships_by_receiver
from ManagementSystem.ext.database.users import get_users_by_role, get_user_by_id, update_main_data, delete_user, \
    update_new_user, update_user, get_users, check_user_by_phone, get_user_by_phone_number
from ManagementSystem.ext.logistics import auto_redirect, check_session
from ManagementSystem.ext.models.flask_session import get_info_by_ip
from ManagementSystem.ext.models.userModel import Role, Reward
from ManagementSystem.ext.telegram_bot.message import send_news
from ManagementSystem.ext.tools import shabbat, get_random_color, set_records, get_friends, normal_phone_number, \
    get_month

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
                            if resp_status:
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
                                flash('Не удалось обработать данные.', 'warning')
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
                            if resp_status:
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
                                flash('Не удалось обработать данные.', 'warning')
                        else:
                            flash('Недопустимый тип файла.', 'warning')
                except Exception as ex:
                    flash('Не удалось изменить изображение.', 'warning')
                    logger.error(ex)

            elif request.form['btn_news'] == 'delete_record':
                rec_id = request.form.get("record_id")
                try:
                    resp_status, data = encrypt_id_with_no_digits(str(rec_id))
                    if resp_status:
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
                    else:
                        flash('Не удалось обработать данные.', 'warning')
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


# Уровень:              admin/offers
# База данных:          offers
# HTML:                 offers
@admin.route('/offers', methods=['POST', 'GET'])
@login_required
def admin_offers():
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
            if request.form['btn_offers'] == 'add_offer':
                name = request.form.get('name')
                description = request.form.get('description')
                date = request.form.get('date')
                start_time = request.form.get('start_time')
                finish_time = request.form.get('finish_time')
                reward = request.form.get('reward')
                if len(start_time) > 0 and len(finish_time) > 0:
                    dates = date.replace(' ', '').split('-')
                    start_time = '0' * (2 - len(start_time)) + start_time
                    finish_time = '0' * (2 - len(finish_time)) + finish_time
                    start_date = datetime.strptime(dates[0] + ' ' + start_time, '%m/%d/%Y %H:%M')
                    finish_date = datetime.strptime(dates[1] + ' ' + finish_time, '%m/%d/%Y %H:%M')
                    add_offer(author=current_user.id, name=name, description=description, start=start_date,
                              finish=finish_date, reward=reward)
                    flash('Вы успешно добавили оффер', 'success')
                else:
                    flash('Выберите дату и время', 'warning')
            elif request.form['btn_offers'] == 'delete_offer':
                offer_id = request.form.get('offer_id')
                delete_offer(offer_id)
                flash('Вы успешно удалили оффер', 'success')
        except Exception as ex:
            logger.error(ex)
            flash('Произошла какая-то ошибка', 'error')

    return render_template("admin/other/offers.html", offers=get_offers().data)


# Уровень:              admin/products
# База данных:          products
# HTML:                 products
@admin.route('/products', methods=['POST', 'GET'])
@login_required
def admin_products():
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
            if request.form['btn_products'] == 'add_product':
                name = request.form.get("name")
                info = request.form.get("description")
                price = request.form.get("price")

                inserted_product = add_product(name, info, price)
                flash('Вы добавили товар.', 'success')

                # image
                filename = ''
                try:
                    image = request.files['image']
                    img_type = image.filename.split('.')[-1].lower()
                    if img_type != '':
                        types = ['jpeg', 'jpg', 'png']
                        if img_type in types:
                            resp_status, data = encrypt_id_with_no_digits(str(inserted_product.inserted_id))
                            if resp_status:
                                product_id = data
                                directory = 'storage/products/'
                                files = os.listdir(directory)
                                for file in files:
                                    if product_id == file.split('.')[0]:
                                        filename = file
                                        break
                                if filename != '':
                                    os.remove(directory + filename)
                                filename = product_id + '.' + img_type
                                image.save(directory + filename)
                            else:
                                flash('Не удалось обработать данные.', 'warning')
                        else:
                            flash('Недопустимый тип файла.', 'warning')
                except Exception as ex:
                    flash('Не удалось прикрепить изображение.', 'warning')
                    logger.error(ex)
            elif request.form['btn_products'] == 'edit_product':
                prod_id = request.form.get("product_id")
                name = request.form.get("name")
                info = request.form.get("description")
                price = request.form.get("price")
                update_product(prod_id, name, info, price)
                flash('Вы обновили товар.', 'success')

                # image
                try:
                    image = request.files['image']
                    img_type = image.filename.split('.')[-1].lower()
                    if img_type != '':
                        types = ['jpeg', 'jpg', 'png']
                        if img_type in types:
                            resp_status, data = encrypt_id_with_no_digits(str(prod_id))
                            if resp_status:
                                product_id = data
                                filename = ''
                                directory = 'storage/products/'
                                files = os.listdir(directory)
                                for file in files:
                                    if product_id == file.split('.')[0]:
                                        filename = file
                                        break
                                if filename != '':
                                    os.remove(directory + filename)
                                filename = product_id + '.' + img_type
                                image.save(directory + filename)
                            else:
                                flash('Не удалось обработать данные.', 'warning')
                        else:
                            flash('Недопустимый тип файла.', 'warning')
                except Exception as ex:
                    flash('Не удалось изменить изображение.', 'warning')
                    logger.error(ex)
            elif request.form['btn_products'] == 'delete_product':
                prod_id = request.form.get("product_id")
                try:
                    resp_status, data = encrypt_id_with_no_digits(str(prod_id))
                    if resp_status:
                        product_id = data
                        filename = ''
                        directory = 'storage/products/'
                        files = os.listdir(directory)
                        for file in files:
                            if product_id == file.split('.')[0]:
                                filename = file
                                break
                        if filename != '':
                            os.remove(directory + filename)
                    else:
                        flash('Не удалось обработать данные.', 'warning')
                except Exception as ex:
                    logger.error(ex)

                delete_product(prod_id)
                delete_orders_by_product_id(prod_id)
                flash('Вы удалили товар.', 'success')
            elif request.form['btn_products'] == 'delete_order':
                order_id = request.form.get("order_id")
                delete_order(order_id)
                flash('Вы удалили заказ.', 'success')
            elif request.form['btn_products'] == 'change_status':
                order_id = request.form.get("order_id")
                order_status = request.form.get("order_status")
                update_order(order_id, 'status', order_status)
                flash('Вы изменили статус заказа.', 'success')
        except Exception as ex:
            logger.error(ex)
            flash('Произошла какая-то ошибка', 'error')

    orders = []
    for i in get_orders().data:
        # product
        r = get_product_by_id(i.product)
        product_name = str(i.product)
        if r.success:
            product_name = r.data.name
        # client
        r = get_user_by_id(i.client)
        client_name = str(i.client)
        if r.success:
            client_name = f'{r.data.first_name} {r.data.last_name}'
        orders.append({
            "id": str(i.id),
            "product": {"id": str(i.product),
                        "name": product_name},
            "client": {"id": str(i.client),
                       "name": client_name},
            "timestamp": i.timestamp.strftime("%d.%m.%Y %H:%M:%S"),
            "status": i.status,
            "address": i.address,
            "country": i.country,
            "city": i.city,
            "zip_postal": i.zip_postal,
            "comments": i.comments
        })

    products = []
    for i in get_products().data:
        product_status, product_id = encrypt_id_with_no_digits(str(i.id))
        if product_status:
            products.append({
                'id': f'{product_id}',
                'product_id': str(i.id),
                'name': i.name,
                'info': i.info,
                'price': i.price
            })

    return render_template("admin/other/products.html", orders=orders, products=products)


# Уровень:              users/admins
# База данных:          User
# HTML:                 admins
@admin.route('/users-admins', methods=['POST', 'GET'])
@login_required
def users_admins():
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
            pass
        except Exception as ex:
            logger.error(ex)
            flash('Произошла какая-то ошибка', 'error')

    return render_template("admin/users/admins.html", admins=get_users_by_role(Role.ADMIN).data)


# Уровень:              users/teachers
# База данных:          User
# HTML:                 teachers
@admin.route('/users-teachers', methods=['POST', 'GET'])
@login_required
def users_teachers():
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
            pass
        except Exception as ex:
            logger.error(ex)
            flash('Произошла какая-то ошибка', 'error')

    return render_template("admin/users/teachers.html", teachers=get_users_by_role(Role.TEACHER).data)


# Уровень:              users/students
# База данных:          User
# HTML:                 students
@admin.route('/users-students', methods=['POST', 'GET'])
@login_required
def users_students():
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
            pass
        except Exception as ex:
            logger.error(ex)
            flash('Произошла какая-то ошибка', 'error')

    students = []
    for i in get_users_by_role(Role.STUDENT).data:
        students.append({
            "id": f'<a href="{url_for("admin.users_student_profile", user_id=i.id)}" target="_blank">{i.id}</a>',
            "phone_number": i.phone_number,
            "first_name": i.first_name,
            "last_name": i.last_name,
            "reward": i.reward.value,
            "birthday": i.birthday
        })

    return render_template("admin/users/students.html", students=students)


# Уровень:              users/students/<user_id>
# База данных:          User
# HTML:                 student-profile
@admin.route('/users-students/<user_id>', methods=['POST', 'GET'])
@login_required
def users_student_profile(user_id):
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
            if request.form['btn_aus'] == 'edit':
                first_name = request.form.get("first_name")
                last_name = request.form.get("last_name")
                phone_number = normal_phone_number(request.form.get("phone_number"))
                birthday = request.form.get("birthday")
                reward = request.form.get("reward")

                r = get_user_by_phone_number(phone_number)
                if r.success:
                    if str(r.data.id) != user_id:
                        # пользователь уже существует
                        flash('Аккаунт с таким номером телефона уже существует!', 'warning')
                        return redirect(url_for('admin.users_student_profile', user_id=user_id))

                update_main_data(user_id, first_name, last_name, phone_number, birthday, reward)
                flash('Вы успешно изменили данные пользователя', 'success')
                return redirect(url_for('admin.users_student_profile', user_id=user_id))
        except Exception as ex:
            logger.error(ex)
            flash('Произошла какая-то ошибка', 'error')

    try:
        resp_user = get_user_by_id(user_id)
        resp = get_attendances_by_user_id(user_id)
        if not resp_user.success or not resp.success:
            return render_template("error-500.html")
        user = resp_user.data
        if user.role != Role.STUDENT:
            return redirect(url_for('networking.profile', user_id=user_id))
        attendance = resp.data
        visits_count = len(attendance)
        # base set up
        now = datetime.now()
        visits_aim = '∞'
        percent = 0
        progress_color = 'bg-dark'
        frequency = '∞'
        extra_info = f'Награда: {user.reward.value}'
        visits_dataset = []
        # TRIP set up
        if user.reward == Reward.TRIP:
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
                    extra_info += f'Необходимо минимум {25 - visits_count} посещений. '
                    if visits_count + weeks_remaining < 25:
                        extra_info += f'Если студент будет ходить раз в неделю, то НЕ сможет выполнить план, поэтому ему надо ходить на отработки/доп занятия. '
                    else:
                        extra_info += f'Если студент будет ходить раз в неделю, то сможет с легкостью выполнить план. '
                else:
                    extra_info += f'Посещаемость в норме. '
            else:
                if visits_count < 30:
                    extra_info = f'Необходимо минимум {30 - visits_count} посещений. '
                else:
                    extra_info = f'Посещаемость в норме. '
        # GRANT set up
        elif user.reward == Reward.GRANT:
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
                extra_info = f'Необходимо посетить еще {visits_aim - visits_count} занятий для получения стипендии в размере: 65$'
            elif visits_count < 7:
                extra_info = f'Есть возможность увеличить стипендию до {65 + 15 * (visits_count + 1 - 4)}$. На данный момент стипендия составляет целых {65 + 15 * (visits_count - 4)}$'
            elif visits_count == 7:
                extra_info = f'Есть возможность увеличить стипендию до 130$. На данный момент стипендия составляет целых {65 + 15 * (visits_count - 4)}$'
            elif visits_count == 8:
                extra_info = f'Стипендия составляет целых 130$'
            else:
                extra_info = f'Посещаемость идеальна :)'
    except Exception as ex:
        logger.error(ex)
        return render_template("error-500.html")

    return render_template("admin/users/student-profile.html", user=user, friends=get_friends(str(user_id)),
                           visits_count=visits_count, visits_aim=visits_aim,
                           progress_color=progress_color, percent=percent, frequency=frequency,
                           extra_info=extra_info,
                           visits_dataset=visits_dataset)


# Уровень:              users/registered
# База данных:          User
# HTML:                 registered
@admin.route('/users-registered', methods=['POST', 'GET'])
@login_required
def users_registered():
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
            if request.form['btn_registered'] == 'add':
                user_id = request.form.get("user_id")
                first_name = request.form.get("first_name")
                last_name = request.form.get("last_name")
                birthday = request.form.get("birthday")
                role = request.form.get("role")
                update_new_user(user_id, first_name, last_name, birthday, role)
                flash('Вы успешно добавили нового пользователя', 'success')
                return redirect(url_for('networking.profile', user_id=user_id))
            elif request.form['btn_registered'] == 'delete':
                user_id = request.form.get("user_id")
                delete_user(user_id)
                flash('Вы успешно отклонили заявку пользователя', 'success')
                return redirect(url_for('admin.users_registered'))
        except Exception as ex:
            logger.error(ex)
            flash('Произошла какая-то ошибка', 'error')

    registered = []
    for i in get_users_by_role(Role.REGISTERED).data:
        # str необходим для избежания исключений с None
        registered.append({
            "id": str(i.id),
            "phone_number": str(i.phone_number),
            "first_name": str(i.first_name),
            "last_name": str(i.last_name),
            "birthday": str(i.birthday)
        })

    return render_template("admin/users/registered.html", registered=registered)


# security block

# Уровень:              security/users
# База данных:          Users
# HTML:                 users
@admin.route('/security/users', methods=['POST', 'GET'])
@login_required
def security_users():
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
            pass
        except Exception as ex:
            logger.error(ex)
            flash('Произошла какая-то ошибка', 'error')

    users = []
    for i in get_users().data:
        # str необходим для избежания исключений с None
        users.append({
            "id": f'<a href="{url_for("networking.profile", user_id=i.id)}" target="_blank">{i.id}</a>',
            "user_id": str(i.id),
            "phone_number": str(i.phone_number),
            "first_name": str(i.first_name),
            "last_name": str(i.last_name),
            "birthday": str(i.birthday)
        })

    return render_template("admin/security/users.html", users=users)


# Уровень:              /security/users/auth
# База данных:          User
# HTML:                 -
@admin.route('/security/users/auth', methods=['POST'])
def security_users_auth():
    try:
        user_id = request.form['user_id']
        user = get_user_by_id(user_id)
        if user.success:
            delete_flask_session(session.get('_id'))
            logout_user()
            login_user(user.data)
            add_flask_session(id=session.get('_id'),
                              user_id=session.get('_user_id'),
                              user_agent=request.user_agent,
                              fresh=session.get('_fresh'),
                              ip=get_info_by_ip(request.remote_addr))
            update_user(user.data.id, 'access_token', '')
            return json.dumps({'success': True, 'url': request.host_url + 'login'}), 200, {
                'ContentType': 'application/json'}
    except Exception as ex:
        logger.error(ex)
    return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}


# Уровень:              /security/users/delete
# База данных:          User
# HTML:                 -
@admin.route('/security/users/delete', methods=['POST'])
def security_users_delete():
    try:
        user_id = request.form['user_id']
        delete_flask_sessions_by_user_id(user_id)
        delete_offers_by_user_id(user_id)
        delete_orders_by_user_id(user_id)
        delete_records_by_user_id(user_id)
        try:
            recs = []
            for rec in get_records_by_author(user_id).data:
                resp_status, data = encrypt_id_with_no_digits(str(user_id))
                if resp_status:
                    recs.append(data)
            directory = 'storage/records/'
            files = os.listdir(directory)
            for file in files:
                if file.split('.')[0] in recs:
                    os.remove(directory + file)
        except Exception as ex:
            logger.error(ex)
        delete_recovers_by_user_id(user_id)
        for i in get_relationships_by_sender(user_id).data:
            delete_relationship(i.id)
        for i in get_relationships_by_receiver(user_id).data:
            delete_relationship(i.id)
        for i in get_courses_by_teacher(user_id).data:
            teachers = []
            for teacher in i.teachers:
                if str(teacher.id) != user_id:
                    teachers.append(str(teacher.id))
            update_course_teachers(teachers)
        delete_user(user_id)
        try:
            resp_status, data = encrypt_id_with_no_digits(str(user_id))
            if resp_status:
                filename = ''
                directory = 'storage/avatars/'
                files = os.listdir(directory)
                for file in files:
                    if data == file.split('.')[0]:
                        filename = file
                        break
                if filename != '':
                    os.remove(directory + filename)
        except Exception as ex:
            logger.error(ex)
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    except Exception as ex:
        return json.dumps({'success': False, 'error': ex}), 200, {'ContentType': 'application/json'}


# Уровень:              security/recovers
# База данных:          recovers
# HTML:                 recovers
@admin.route('/security/recovers', methods=['POST', 'GET'])
@login_required
def security_recovers():
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
            if request.form['btn_recovers'] == 'delete_recover':
                recover_id = request.form.get("recover_id")
                delete_recover(recover_id)
                flash('Вы удалили запрос.', 'success')
        except Exception as ex:
            logger.error(ex)
            flash('Произошла какая-то ошибка', 'error')

    return render_template("admin/security/recovers.html", recovers=get_recovers().data)


# Уровень:              /security/recovers/link
# База данных:          User
# HTML:                 -
@admin.route('/security/recovers/link', methods=['POST'])
def security_recover_link():
    try:
        recover_id = request.form['recover_id']
        user_id = request.form['user_id']
        status, token = create_token()
        if status:
            update_user(user_id, 'access_token', token)
            recover_url = request.host_url + 'login/' + token
            delete_recover(recover_id)
            return json.dumps({'success': True, 'url': recover_url}), 200, {'ContentType': 'application/json'}
    except Exception as ex:
        pass
    return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}


# Уровень:              security/sessions
# База данных:          flask_sessions
# HTML:                 sessions
@admin.route('/security/sessions', methods=['POST', 'GET'])
@login_required
def security_sessions():
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
            pass
        except Exception as ex:
            logger.error(ex)
            flash('Произошла какая-то ошибка', 'error')

    sessions = []
    for i in get_flask_sessions().data:
        # str необходим для избежания исключений с None
        sessions.append({
            "id": str(i.id),
            "short_id": f'{i.id[:10]}...',
            "user_id": f'<a href="{url_for("networking.profile", user_id=i.user_id)}" target="_blank">{i.user_id}</a>',
            "user_agent": i.user_agent,
            "ip": i.ip,
        })

    return render_template("admin/security/sessions.html", sessions=sessions)


# Уровень:              /security/session/delete
# База данных:          flask-sessions
# HTML:                 -
@admin.route('/security/session/delete', methods=['POST'])
def security_session_delete():
    try:
        session_id = request.form['id']
        delete_flask_session(session_id)
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    except Exception as ex:
        return json.dumps({'success': False, 'error': ex}), 200, {'ContentType': 'application/json'}


# Уровень:              security/database
# База данных:          Any
# HTML:                 database
@admin.route('/security/database', methods=['POST', 'GET'])
@login_required
def security_database():
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
            if request.form['database'] == 'users':
                id = request.form.get("id_user")
                key = request.form.get("field_user")
                value = request.form.get("value_user")

                if key == 'phone_number':
                    if check_user_by_phone(value):
                        # пользователь уже существует
                        flash('Аккаунт с таким номером телефона уже существует!', 'warning')
                        return redirect(url_for('admin.security_database'))
                    npn = normal_phone_number(value)
                    if len(npn) != 11 or not npn.startswith('8'):
                        flash('Номер телефона не соответствует формату!', 'warning')
                        return redirect(url_for('admin.security_database'))
                elif key == 'role':
                    if value not in ['student', 'admin', 'teacher', 'registered', 'null']:
                        flash(
                            "Роль должна быть одним из след. значений: 'student', 'admin', 'teacher', 'registered', 'null'",
                            'warning')
                        return redirect(url_for('admin.security_database'))
                elif key == 'reward':
                    if value not in ['trip', 'grant', 'null']:
                        flash("Награда должна быть одним из след. значений: 'trip', 'grant', 'null'", 'warning')
                        return redirect(url_for('admin.security_database'))
                update_user(id, key, value)
                flash('Данные пользователя обновлены', 'success')

        except Exception as ex:
            logger.error(ex)
            flash(str(ex), 'error')

    return render_template("admin/security/database.html")


# Уровень:              configuration/files
# База данных:
# HTML:
@admin.route('/configuration/files', methods=['POST', 'GET'])
@login_required
def configuration_files():
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
            pass
        except Exception as ex:
            logger.error(ex)
            flash(str(ex), 'error')

    folders = []
    try:
        for file in os.listdir('storage'):
            if os.path.isdir(file):
                folders.append({
                    "name": file,
                    "files": os.listdir(f'storage/{file}/')
                })
    except:
        pass

    return render_template("admin/configuration/files.html", folders=folders)


# Уровень:              configuration/
# База данных:
# HTML:
@admin.route('/configuration/variables', methods=['POST', 'GET'])
@login_required
def configuration_variables():
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
            pass
        except Exception as ex:
            logger.error(ex)
            flash(str(ex), 'error')

    return render_template("admin/configuration/variables.html")


# Уровень:              configuration/
# База данных:
# HTML:
@admin.route('/configuration/backup', methods=['POST', 'GET'])
@login_required
def configuration_backup():
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
            pass
        except Exception as ex:
            logger.error(ex)
            flash(str(ex), 'error')

    return render_template("admin/configuration/backup.html")
