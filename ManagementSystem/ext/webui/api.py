import os
from logging import getLogger

from flask import *

from ManagementSystem.ext.database.attendances import get_attendances_by_user_id
from ManagementSystem.ext.database.courses import get_courses, Time
from ManagementSystem.ext.database.offers import get_offers
from ManagementSystem.ext.database.products import get_products
from ManagementSystem.ext.database.records import get_records_by_type, RecordType
from ManagementSystem.ext.database.relationships import get_relationships_by_sender
from ManagementSystem.ext.database.users import get_users, get_user_by_id
from ManagementSystem.ext.search_engine import search_documents
from ManagementSystem.ext.tools import encrypt_id_with_no_digits, bfs, get_random_color, get_friends, set_records

logger = getLogger(__name__)  # logging
api = Blueprint('api', __name__, url_prefix='/api', template_folder='templates', static_folder='assets')


# Уровень:              avatar/user_id
# База данных:          storage/avatars
# HTML:                 -
@api.route('/avatar/<user_id>', methods=['POST', 'GET'])
def get_avatar(user_id):
    filename = 'undraw_avatar.png'
    directory = 'storage/avatars/'
    resp_status, data = encrypt_id_with_no_digits(str(user_id))
    if resp_status:
        try:
            files = os.listdir(directory)
            for file in files:
                if data == file.split('.')[0]:
                    filename = file
                    break
        except Exception as ex:
            logger.error(ex)
    return send_file(directory + filename)


# Уровень:              record/record_id
# База данных:          storage/records
# HTML:                 -
@api.route('/record/<record_id>', methods=['POST', 'GET'])
def get_record_image(record_id):
    filename = ''
    directory = 'storage/records/'
    resp_status, data = encrypt_id_with_no_digits(str(record_id))
    if resp_status:
        try:
            files = os.listdir(directory)
            for file in files:
                if data == file.split('.')[0]:
                    filename = file
                    break
        except Exception as ex:
            logger.error(ex)
    if filename == '':
        return json.dumps({'info': 'image not found'}), 200, {
            'ContentType': 'application/json'}
    return send_file(directory + filename)


# Уровень:              product/product_id
# База данных:          storage/products
# HTML:                 -
@api.route('/product/<product_id>', methods=['POST', 'GET'])
def get_product_image(product_id):
    filename = ''
    directory = 'storage/products/'
    try:
        files = os.listdir(directory)
        for file in files:
            if str(product_id) == file.split('.')[0]:
                filename = file
                break
    except Exception as ex:
        logger.error(ex)
    if filename == '':
        return json.dumps({'info': 'image not found'}), 200, {
            'ContentType': 'application/json'}
    return send_file(directory + filename)


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
        logger.error(ex)
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
        logger.error(ex)
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
        logger.error(ex)
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
        logger.error(ex)
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
        logger.error(ex)
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
        logger.error(ex)
    return json.dumps({'data': ''}), 200, {'ContentType': 'application/json'}


# Уровень:              offers/count
# База данных:          Offers
# HTML:                 -
@api.route('/records/count', methods=['POST'])
def records_count():
    try:
        news = len(get_records_by_type(RecordType.NEWS).data)
        notifications = len(get_records_by_type(RecordType.NOTIFICATION).data)
        return json.dumps({'success': True, 'news': news, 'notifications': notifications}), 200, {
            'ContentType': 'application/json'}
    except Exception as ex:
        logger.error(ex)
        return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}


# Уровень:              attendance/count
# База данных:          attendance
# HTML:                 -
@api.route('/attendance/count/<user_id>', methods=['POST'])
def attendance_count(user_id):
    try:
        cnt = len(get_attendances_by_user_id(user_id).data)
        if cnt > 0:
            return json.dumps({'data': cnt}), 200, {'ContentType': 'application/json'}
    except Exception as ex:
        logger.error(ex)
    return json.dumps({'data': ''}), 200, {'ContentType': 'application/json'}


# Уровень:              api/notifications
# База данных:          Records
# HTML:                 -
@api.route('/notifications', methods=['POST'])
def get_notifications():
    try:
        return json.dumps(
            {'success': True, 'notifications': set_records(get_records_by_type(RecordType.NOTIFICATION))}), 200, {
                   'ContentType': 'application/json'}
    except Exception as ex:
        logger.error(ex)
    return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}
