import os
from datetime import datetime
import logging

from flask import *

from ManagementSystem.ext.notifier import notify_user
from ManagementSystem.ext import directories, valid_images, api_token, system_variables
from ManagementSystem.ext.database.attendances import get_attendances_by_user_id, add_attendance
from ManagementSystem.ext.database.courses import get_courses, Time, get_courses_json
from ManagementSystem.ext.database.flask_sessions import get_flask_sessions
from ManagementSystem.ext.database.offers import get_offers
from ManagementSystem.ext.database.orders import get_orders
from ManagementSystem.ext.database.products import get_products
from ManagementSystem.ext.database.records import get_records_by_type, RecordType, delete_record
from ManagementSystem.ext.database.recover_pw import get_recovers
from ManagementSystem.ext.database.relationships import get_relationships_by_sender
from ManagementSystem.ext.database.users import get_users, get_user_by_id, update_notifications, Reward, Role, \
    get_users_json
from ManagementSystem.ext.search_engine import search_documents
from ManagementSystem.ext.snapshotting import backup, restore, get_sorted_backups
from ManagementSystem.ext.tools import encrypt_id_with_no_digits, bfs, get_random_color, get_friends, get_month

api = Blueprint('api', __name__, url_prefix='/api', template_folder='templates', static_folder='assets')


# Уровень:              avatar/user_id
# База данных:          storage/database/avatars
# HTML:                 -
@api.route('/avatar/<user_id>', methods=['POST', 'GET'])
def get_avatar(user_id):
    filename = 'undraw_avatar.png'
    directory = directories['avatars']
    resp_status, data = encrypt_id_with_no_digits(str(user_id))
    if resp_status:
        try:
            files = os.listdir(directory)
            for file in files:
                if data == file.split('.')[0]:
                    filename = file
                    break
        except Exception as ex:
            logging.error(f'get_avatar: {ex}')
    return send_file(os.path.join(directory, filename))


# Уровень:              record/record_id
# База данных:          storage/database/records
# HTML:                 -
@api.route('/record/<record_id>', methods=['POST', 'GET'])
def get_record_image(record_id):
    filename = ''
    directory = directories['records']
    resp_status, data = encrypt_id_with_no_digits(str(record_id))
    if resp_status:
        try:
            files = os.listdir(directory)
            for file in files:
                if data == file.split('.')[0]:
                    filename = file
                    break
        except Exception as ex:
            logging.error(f'get_record_image: {ex}')
    if filename == '':
        return json.dumps({'info': 'image not found'}), 200, {
            'ContentType': 'application/json'}
    return send_file(os.path.join(directory, filename))


# Уровень:              product/product_id
# База данных:          storage/database/products
# HTML:                 -
@api.route('/product/<product_id>', methods=['POST', 'GET'])
def get_product_image(product_id):
    filename = ''
    directory = directories['products']
    resp_status, data = encrypt_id_with_no_digits(str(product_id))
    if resp_status:
        try:
            files = os.listdir(directory)
            for file in files:
                if data == file.split('.')[0]:
                    filename = file
                    break
        except Exception as ex:
            logging.error(f'get_product_image: {ex}')
    if filename == '':
        return json.dumps({'info': 'image not found'}), 200, {
            'ContentType': 'application/json'}
    return send_file(os.path.join(directory, filename))


# Уровень:              storage/database/<folder>/<filename>
# База данных:          storage/*
# HTML:                 -
@api.route('/storage/<folder>/<filename>', methods=['POST', 'GET'])
def get_image(folder, filename):
    if folder not in directories:
        return json.dumps({'success': False, "info": "Unknown folder."}), 200, {'ContentType': 'application/json'}
    if filename.split('.')[-1] not in valid_images:
        return json.dumps({'success': False, "info": "Invalid file type."}), 200, {'ContentType': 'application/json'}
    return send_file(f'storage/database/{folder}/{filename}')


# NET WORKING


# Уровень:              networking/dataset
# База данных:          User, Relations
# HTML:                 -
@api.route('/networking/dataset', methods=['POST'])
def networking_dataset():
    try:
        resp = get_users()
        if not resp.success:
            return json.dumps({'success': False}), 200, {
                'ContentType': 'application/json'}
        else:
            users = resp.data
            nodes = []
            edges = []
            for user in users:
                r = get_relationships_by_sender(user.id)
                if r.success:
                    friends = get_friends(str(user.id))
                    if len(friends) > 0:
                        nodes.append({"id": str(user.id), "shape": "circularImage",
                                      "image": url_for('api.get_avatar', user_id=user.id)})
                        for friend in friends:
                            if not {"from": str(friend), "to": str(user.id)} in edges:
                                edges.append({"from": str(user.id), "to": str(friend)})
            return json.dumps({'success': True, 'nodes': nodes, 'edges': edges}), 200, {
                'ContentType': 'application/json'}
    except Exception as ex:
        logging.error(f'networking_dataset: {ex}')
        return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}


# Уровень:              networking/way
# База данных:          User, Relations
# HTML:                 -
@api.route('/networking/way', methods=['POST'])
def networking_way():
    try:
        start_vertex = request.form['startVertex']
        finishVertex = request.form['finishVertex']
        resp = get_users()
        if not resp.success:
            return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}
        else:
            users = resp.data
            way = bfs(start_vertex, finishVertex, users)
            return json.dumps({'success': True, 'way': way}), 200, {
                'ContentType': 'application/json'}
    except Exception as ex:
        logging.error(f'networking_way: {ex}')
        return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}


# Уровень:              networking/search
# База данных:          User, Relations
# HTML:                 -
@api.route('/networking/search', methods=['POST'])
def networking_search():
    try:
        query = request.form['query']
        users = get_users().data
        if len(query) != 0:
            docs = [user.to_document() for user in users]
            result = search_documents(documents=docs, query=query, max_result_document_count=-1)
            users = list(filter(lambda user: str(user.id) in result, users))
            users.sort(key=lambda user: result.index(str(user.id)))
        return json.dumps({'success': True, 'users': [user.to_net() for user in users]}), 200, {
            'ContentType': 'application/json'}
    except Exception as ex:
        logging.error(f'networking_search: {ex}')
        return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}


# Уровень:              api/schedule/timetable
# База данных:          Courses
# HTML:                 -
@api.route('/courses/schedule/timetable', methods=['POST'])
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
                            teachers.append(
                                f'<a href="{url_for("networking.profile", user_id=r.data.id)}" target="_blank">{r.data.first_name} {r.data.last_name}</a>')
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
                {'success': True, 'times': times, 'courses': filtered_courses,
                 'colors': colors}), 200, {
                       'ContentType': 'application/json'}
    except Exception as ex:
        logging.error(f'get_schedule: {ex}')
    return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}


# Уровень:              offers/count
# База данных:          Offers
# HTML:                 -
@api.route('/offers/count', methods=['POST'])
def offers_count():
    try:
        cnt = len(get_offers().data)
        if cnt > 0:
            return json.dumps({'data': cnt}), 200, {'ContentType': 'application/json'}
    except Exception as ex:
        logging.error(f'offers_count: {ex}')
    return json.dumps({'data': ''}), 200, {'ContentType': 'application/json'}


# Уровень:              products/count
# База данных:          Products
# HTML:                 -
@api.route('/products/count', methods=['POST'])
def products_count():
    try:
        cnt = len(get_products().data)
        if cnt > 0:
            return json.dumps({'data': cnt}), 200, {'ContentType': 'application/json'}
    except Exception as ex:
        logging.error(f'products_count: {ex}')
    return json.dumps({'data': ''}), 200, {'ContentType': 'application/json'}


# Уровень:              orders/count
# База данных:          Orders
# HTML:                 -
@api.route('/orders/count', methods=['POST'])
def orders_count():
    try:
        cnt = len(get_orders().data)
        if cnt > 0:
            return json.dumps({'data': cnt}), 200, {'ContentType': 'application/json'}
    except Exception as ex:
        logging.error(f'orders_count: {ex}')
    return json.dumps({'data': ''}), 200, {'ContentType': 'application/json'}


# Уровень:              offers/count
# База данных:          Offers
# HTML:                 -
@api.route('/records/count', methods=['POST'])
def records_count():
    try:
        news = len(get_records_by_type(RecordType.NEWS).data)
        return json.dumps({'success': True, 'news': news}), 200, {
            'ContentType': 'application/json'}
    except Exception as ex:
        logging.error(f'records_count: {ex}')
        return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}


# Уровень:              offers/count
# База данных:          Offers
# HTML:                 -
@api.route('/security/count', methods=['POST'])
def security_count():
    try:
        users = len(get_users().data)
        recovers = len(get_recovers().data)
        sessions = len(get_flask_sessions().data)
        return json.dumps({'success': True, 'users': users, 'recovers': recovers, 'sessions': sessions}), 200, {
            'ContentType': 'application/json'}
    except Exception as ex:
        logging.error(f'security_count: {ex}')
        return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}


# Уровень:              attendance/count
# База данных:          attendance
# HTML:                 -
@api.route('/attendance/count/<user_id>', methods=['POST'])
def attendance_count(user_id):
    try:
        cnt = 0
        now = datetime.now()
        current_year = now.year
        if now.month >= 9:
            start = current_year
            end = current_year + 1
        else:
            start = current_year - 1
            end = current_year
        for i in get_attendances_by_user_id(user_id).data:
            date = i.date
            if (date.year == start and date.month >= 9) or (date.year == end and date.month < 9):
                cnt += i.count
        if cnt > 0:
            return json.dumps({'data': cnt}), 200, {'ContentType': 'application/json'}
    except Exception as ex:
        logging.error(f'attendance_count: {ex}')
    return json.dumps({'data': ''}), 200, {'ContentType': 'application/json'}


# Уровень:              attendance/get
# База данных:          attendances, users
# HTML:                 -
@api.route('/attendance/get/user', methods=['POST'])
def get_user_attendance():
    try:
        user_id = request.form['user_id']
        start = int(request.form['start'])
        end = int(request.form['end'])

        d = {
            "september": [],
            "october": [],
            "november": [],
            "december": [],
            "january": [],
            "february": [],
            "march": [],
            "april": [],
            "may": []
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
            5: 'may'
        }

        for i in get_attendances_by_user_id(user_id).data:
            date = i.date
            if (date.year == start and date.month >= 9) or (date.year == end and date.month < 9):
                if date.month in months.keys():
                    d[months[date.month]].append(
                        {"id": str(i.id), "date": date.strftime("%d.%m.%Y %H:%M:%S"), "count": i.count})

        return json.dumps({'success': True, 'data': d}), 200, {
            'ContentType': 'application/json'}
    except Exception as ex:
        logging.error(f'get_user_attendance: {ex}')
    return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}


# Уровень:              notifications/clear/all
# База данных:          users
# HTML:                 -
@api.route('/notifications/clear/all', methods=['POST'])
def clear_notifications():
    try:
        user_id = request.form['user_id']
        update_notifications(user_id, [])
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    except Exception as ex:
        logging.error(f'clear_notifications: {ex}')
    return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}


# Уровень:              notifications/delete
# База данных:          users
# HTML:                 -
@api.route('/notifications/delete', methods=['POST'])
def delete_notification():
    try:
        user_id = request.form['user_id']
        notification_id = request.form['notification_id']
        r = get_user_by_id(user_id)
        if r.success:
            notification = None
            notifications = r.data.notifications
            for i in notifications:
                if notification_id == i.id:
                    notification = i
                    break
            if notification is not None:
                notifications.remove(notification)
                update_notifications(user_id, notifications)
            return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    except Exception as ex:
        logging.error(f'delete_notification: {ex}')
    return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}


# API with TOKEN

# Уровень:              snapshot/dump
# База данных:          All
# HTML:                 -
@api.route('/snapshot/dump', methods=['POST'])
def snapshot_dump():
    token = request.json['token']
    status = False
    if token == api_token:
        status, filename = backup()
        from ManagementSystem.ext.telegram.message import send_file
        chat_id = request.json['chat_id']
        if chat_id != '':
            send_file(filename, chat_id)
    return json.dumps({'success': status}), 200, {'ContentType': 'application/json'}


# Уровень:              snapshot/restore
# База данных:          All
# HTML:                 -
@api.route('/snapshot/restore', methods=['POST'])
def snapshot_restore():
    token = request.json['token']
    status = False
    if token == api_token:
        filename = request.json['file']
        status = restore(filename)
    return json.dumps({'success': status}), 200, {'ContentType': 'application/json'}


# Уровень:              snapshot/backups
# База данных:          All
# HTML:                 -
@api.route('/snapshot/backups', methods=['POST'])
def snapshot_backups():
    token = request.json['token']
    if token == api_token:
        files = get_sorted_backups()
        return json.dumps({'success': True, 'files': files}), 200, {'ContentType': 'application/json'}
    return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}


# Уровень:              attendance/admin
# База данных:          Attendance
# HTML:                 -
@api.route('/attendance/admin', methods=['POST'])
def attendance_admin():
    try:
        token = request.json['token']
        if token == api_token:
            now = datetime.now()
            current_year = now.year
            if now.month >= 9:
                start = current_year
                end = current_year + 1
            else:
                start = current_year - 1
                end = current_year
            users_with_bad_attendance = list()
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
                5: 'may'
            }
            if now <= trip_date:
                for user in get_users().data:
                    try:
                        if user.role == Role.STUDENT and user.reward == Reward.TRIP:
                            visits_count = 0
                            for i in get_attendances_by_user_id(user.id).data:
                                date = i.date
                                if (date.year == start and date.month >= 9) or (
                                        date.year == end and date.month < 9):
                                    if date.month in months.keys():
                                        visits_count += 1
                            if visits_count + weeks_remaining < 25:
                                users_with_bad_attendance.append({
                                    "name": f'{user.first_name} {user.last_name}',
                                    "href": f'{request.url_root[:-1]}{url_for("admin.user_attendance", user_id=str(user.id))}',
                                    "visits": visits_count
                                })
                    except:
                        pass
            return json.dumps({'success': True, 'data': users_with_bad_attendance}), 200, {
                'ContentType': 'application/json'}
    except:
        pass
    return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}


# Уровень:              attendance/student
# База данных:          Attendance
# HTML:                 -
@api.route('/attendance/student', methods=['POST'])
def attendance_student():
    try:
        token = request.json['token']
        status = False
        if token == api_token:
            user_id = request.json['user_id']

            now = datetime.now()
            current_year = now.year
            if now.month >= 9:
                start = current_year
                end = current_year + 1
            else:
                start = current_year - 1
                end = current_year

            resp = get_user_by_id(user_id)
            if not resp.success:
                return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}

            user = resp.data
            if user.role != Role.STUDENT:
                return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}

            resp = get_attendances_by_user_id(user_id)
            if not resp.success:
                return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}

            attendance = []
            for i in resp.data:
                date = i.date
                if (date.year == start and date.month >= 9) or (date.year == end and date.month < 9):
                    attendance.append(i)

            visits_count = len(attendance)
            # base set up
            visits_aim = '∞'
            percent = 0
            frequency = '∞'
            extra_info = f'Ваша награда: {user.reward.value}'
            visits_dataset = []
            # TRIP set up
            if user.reward == Reward.TRIP:
                visits_aim = 30
                percent = int(visits_count / visits_aim * 100)
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
            return json.dumps({'success': True,
                               "data": {"visits_count": visits_count, "visits_aim": visits_aim, "percent": percent,
                                        "frequency": frequency, "extra_info": extra_info,
                                        "visits_dataset": visits_dataset,
                                        "href": f'{request.url_root[:-1]}{url_for("student.student_attendance")}'}}), 200, {
                       'ContentType': 'application/json'}
    except:
        pass
    return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}


# Уровень:              attendance/update
# База данных:          Attendance
# HTML:                 -
@api.route('/attendance/update', methods=['POST'])
def attendance_update():
    try:
        token = request.json['token']
        status = False
        if token == api_token:
            user_id = request.json['user_id']
            date = request.json['date']
            count = request.json['count']
            r = get_user_by_id(user_id)
            if r.success:
                user = r.data
                if user.role == Role.STUDENT and user.reward != Reward.NULL:
                    count = int(count)
                    if count > 0:
                        add_attendance(user_id, count, date)
                        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    except:
        pass
    return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}


# Уровень:              records/delete
# База данных:          records
# HTML:                 -
@api.route('/records/delete', methods=['POST'])
def records_delete():
    token = request.json['token']
    if token == api_token:
        record_id = request.json['record_id']
        user_id = request.json['user_id']
        try:
            resp_status, crypted_record_id = encrypt_id_with_no_digits(str(record_id))
            if resp_status:
                filename = ''
                directory = directories['records']
                files = os.listdir(directory)
                for file in files:
                    if crypted_record_id == file.split('.')[0]:
                        filename = file
                        break
                if filename != '':
                    os.remove(os.path.join(directory, filename))
        except Exception as ex:
            logging.error(ex)
        delete_record(record_id)
        notify_user(user_id, 'Удалена запись', '', 'mdi mdi-delete-clock', 'primary',
                    f'Удалена одна из ваших записей, у которой вы установили временное ограничение.')
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}


# Уровень:              users
# База данных:          users
# HTML:                 -
@api.route('/users', methods=['POST'])
def api_get_users():
    try:
        token = request.json['token']
        if token == api_token:
            return json.dumps({'success': True, 'data': get_users_json()}), 200, {'ContentType': 'application/json'}
    except Exception as ex:
        print(ex)
        pass
    return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}


# Уровень:              courses
# База данных:          courses
# HTML:                 -
@api.route('/courses', methods=['POST'])
def api_get_courses():
    try:
        token = request.json['token']
        if token == api_token:
            return json.dumps({'success': True, 'data': get_courses_json()}), 200, {'ContentType': 'application/json'}
    except:
        pass
    return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}
