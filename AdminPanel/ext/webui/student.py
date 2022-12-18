import os

from AdminPanel.ext.database.users import *
from AdminPanel.ext.models.recover_pw import *
from flask import *
from flask_toastr import *
from flask_login import *
from AdminPanel.ext.crypt import *
import logging

logger = logging.getLogger(__name__)  # logging
student = Blueprint('student', __name__, url_prefix='/student', template_folder='templates/student',
                    static_folder='assets')


def auto_redirect(ignore_role=Role.NULL):
    if current_user.is_authenticated:
        if current_user.role == ignore_role:
            return False, None
        if current_user.role == Role.REGISTERED:
            return True, "/registered"
        elif current_user.role == Role.STUDENT:
            return True, "/student/home"
        elif current_user.role == Role.TEACHER:
            return True, "/teacher/home"
        elif current_user.role == Role.ADMIN:
            return True, "/admin/home"
    return False, None


# Уровень:              Главная страница
# База данных:          User
# HTML:                 home
@student.route('/')
@student.route('/home', methods=['POST', 'GET'])
@login_required
def student_home():
    status, url = auto_redirect(ignore_role=Role.STUDENT)
    if status:
        return redirect(url)
    return render_template("home.html")


# Уровень:              Главная страница
# База данных:          User
# HTML:                 account
@student.route('/account', methods=['POST', 'GET'])
@login_required
def student_account():
    status, url = auto_redirect(ignore_role=Role.STUDENT)
    if status:
        return redirect(url)
    if request.method == "POST":
        avatar = request.files['avatar']
        img_type = avatar.filename.split('.')[-1]
        types = ['jpeg', 'jpg', 'png']
        if img_type in types:
            try:
                phone_number = current_user.phone_number
                filename = ''
                directory = 'storage/avatars/'
                files = os.listdir(directory)
                for file in files:
                    if phone_number == file.split('.')[0]:
                        filename = file
                        break
                if filename != '':
                    os.remove(directory + filename)
                avatar.save(directory + phone_number + '.' + img_type)
            except Exception as ex:
                logger.error(ex)
            flash('Аватарка успешно обновлена', category='success')
        else:
            flash('Такое расширение файла не подходит', category='warning')
    return render_template("account.html")


# Уровень:              account/avatar
# База данных:          storage/avatars
# HTML:                 -
@student.route('account/avatar', methods=['POST', 'GET'])
def get_avatar():
    filename = 'undraw_avatar.jpg'
    directory = 'storage/avatars/'
    try:
        files = os.listdir(directory)
        for file in files:
            if current_user.phone_number == file.split('.')[0]:
                filename = file
                break
    except Exception as ex:
        logger.error(ex)
    return send_file(directory + filename, as_attachment=True)


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
