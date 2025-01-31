import logging
from random import choice

from flask import Blueprint, redirect, request, session, flash, url_for, json, make_response
from flask_login import *
from flask_toastr import *

from ManagementSystem.ext import system_variables, config
from ManagementSystem.ext.crypt import check_password_hash, crypt_pass, create_token
from ManagementSystem.ext.database.flask_sessions import add_flask_session, delete_flask_session, get_info_by_ip, \
    get_flask_sessions_by_user_id
from ManagementSystem.ext.database.recover_pw import add_recover, get_recover_by_phone, delete_recovers_by_user_id
from ManagementSystem.ext.database.users import get_user_by_phone_number, update_user, check_user_by_phone, add_user, \
    Role, update_registered_user, get_user_by_access_token, update_password_by_access_token, get_user_by_id
from ManagementSystem.ext.logistics import auto_redirect, check_session
from ManagementSystem.ext.notifier import notify_admins
from ManagementSystem.ext.telegram.message import send_message
from ManagementSystem.ext.text_filter import TextFilter
from ManagementSystem.ext.tools import normal_phone_number

view = Blueprint('view', __name__, template_folder='templates', static_folder='assets')  # route
temporary_folder = 'storage/broker'


# Уровень:              Главная страница
# База данных:          -
# HTML:                 landing
@view.route('/')
def landing():
    return render_template("landing.html")


# Accounting


# Уровень:              login
# База данных:          User
# HTML:                 auth-login
@view.route('/login', methods=["GET", "POST"])
def login():
    status, url = auto_redirect()
    if status:
        return redirect(url)
    if request.method == "POST":
        try:
            input_phone_number = normal_phone_number(request.form.get("phonenumber"))
            input_password = request.form.get("password")
            user = get_user_by_phone_number(phone_number=input_phone_number)
            if user.success is False:
                flash('Пользователь не найден!', 'warning')
            else:
                if check_password_hash(user.data.password, input_password):
                    # авторизуем пользователя
                    login_user(user.data)
                    user_ip = request.remote_addr
                    session_id = session.get('_id')
                    add_flask_session(id=session_id,
                                      user_id=session.get('_user_id'),
                                      user_agent=request.user_agent,
                                      fresh=session.get('_fresh'),
                                      ip=get_info_by_ip(user_ip))

                    # Получаем исходный URL из сессии или используем страницу по умолчанию
                    next_url = session.get('next_url') or url_for('view.login')
                    # Очищаем исходный URL из сессии
                    session.pop('next_url', None)

                    # Устанавливаем куку с session_id и длительным сроком жизни (например, 1 неделя)
                    response = make_response(redirect(next_url))
                    response.set_cookie('session_id', session_id, max_age=config.flask.session_max_age)

                    update_user(user.data.id, 'access_token', '')
                    flash('Вы успешно авторизовались!', 'success')
                    logging.info(f'авторизован пользователь {input_phone_number}')
                    if user.data.telegram_id is not None:
                        flag = True
                        for flask_session in get_flask_sessions_by_user_id(user.data.id).data:
                            if flask_session.ip['query'] == user_ip:
                                flag = False
                        if flag:
                            msg = f'Совершен вход в ваш аккаунт. (IP: {user_ip})\n' \
                                  'Если это не вы срочно смените пароль в настройках и завершите все сессии.'
                            send_message(msg, user.data.telegram_id)
                    return response
                else:
                    flash('Неверный пароль!', 'warning')
        except Exception as ex:
            logging.error(ex)
    templates = ['auth-login.html', 'auth-login-2.html']  # для случайной генерации шаблона
    return render_template("authentication/" + choice(templates))


# Уровень:              login/<access_token>
# База данных:          User
# HTML:                 -
@view.route('/login/<access_token>', methods=["GET", "POST"])
def tg_login(access_token):
    if len(access_token) != 32:
        return redirect(url_for('view.login'))
    status, url = auto_redirect()
    if status:
        return redirect(url)
    try:
        user = get_user_by_access_token(access_token)
        if user.success:
            delete_flask_session(session.get('_id'))
            logout_user()
            # авторизуем пользователя
            login_user(user.data)

            session_id = session.get('_id')
            add_flask_session(id=session_id,
                              user_id=session.get('_user_id'),
                              user_agent=request.user_agent,
                              fresh=session.get('_fresh'),
                              ip=get_info_by_ip(request.remote_addr))

            # Устанавливаем куку с session_id и длительным сроком жизни (например, 1 неделя)
            response = make_response(redirect(request.args.get("next") or url_for("view.login")))
            response.set_cookie('session_id', session_id, max_age=config.flask.session_max_age)

            flash('Вы успешно авторизовались!', 'success')
            update_user(user.data.id, 'access_token', '')
    except Exception as ex:
        logging.error(ex)
    return redirect(request.args.get("next") or url_for("view.login"))


# Уровень:              logout
# База данных:          -
# HTML:                 auth-logout
@view.route('/logout')
def logout():
    if current_user.is_authenticated:
        delete_flask_session(session.get('_id'))
        logout_user()
        flash("Вы вышли из аккаунта", "success")
        templates = ['auth-logout.html', 'auth-logout-2.html']  # для случайной генерации шаблона

        # Создаем response и удаляем куки с session_id
        response = make_response(render_template("authentication/" + choice(templates)))
        response.delete_cookie('session_id')

        return response
    else:
        return redirect(url_for("view.landing"))


# Уровень:              recoverpw
# База данных:          User
# HTML:                 auth-recoverpw
@view.route('/recoverpw/', methods=["GET", "POST"], defaults={'version': 1})
@view.route('/recoverpw/<version>', methods=["GET", "POST"])
def recoverpw(version):
    status, url = auto_redirect()
    if status:
        return redirect(url)
    if request.method == "POST":
        try:
            input_phone_number = normal_phone_number(request.form.get("phonenumber"))
            user = get_user_by_phone_number(phone_number=input_phone_number)
            if user.success is False:
                flash('Пользователь не найден!', 'warning')
            else:
                if get_recover_by_phone(input_phone_number).success:
                    flash('Вы уже запрашивали смену пароля. Вопрос на рассмотрении у администрации!', 'info')
                else:
                    if user.data.telegram_id is None:
                        add_recover(input_phone_number, user.data.id)
                        flash('Ваш запрос передан администрации на рассмотрение!', 'info')
                        notify_admins('Смена пароля', url_for('admin.security_recovers'), 'mdi mdi-shield-key',
                                      'warning',
                                      f'Пользователь подал заявку на восстановление пароля ID={current_user.id}')
                    else:
                        status, token = create_token()
                        if status:
                            update_user(user.data.id, 'access_token', token)
                            recover_url = request.host_url + 'password/reset/' + token
                            msg = f'Произошел запрос на восстановление доступа к аккаунту.\n' \
                                  f'Перейдите по ссылке и смените пароль.\n' \
                                  f'{recover_url}' \
                                  '\nЕсли это не вы срочно смените пароль в настройках.'
                            send_message(msg, user.data.telegram_id)
                            flash('Наш бот отправит вам ссылку для смены пароля!', 'success')
                        else:
                            flash('Не удалось отправить ссылку на восстановление пароля!', 'warning')
                return redirect("/login")
        except Exception as ex:
            logging.error(ex)
    if version == "2":
        return render_template("authentication/auth-recoverpw-2.html")
    else:
        return render_template("authentication/auth-recoverpw.html")


# Уровень:              /password/reset/<access_token>
# База данных:          User
# HTML:                 auth-reset-password
@view.route('/password/reset/<access_token>', methods=["GET", "POST"])
def reset_password(access_token):
    status, url = auto_redirect()
    if status:
        return redirect(url)

    r = get_user_by_access_token(access_token)
    if not r.success:
        return redirect(url_for("view.landing"))

    if request.method == "POST":
        try:
            password = request.form.get("password")
            password_repeat = request.form.get("password_repeat")
            if len(password) < 4:
                flash('Длина пароля должна быть больше 4.', 'warning')
            elif password != password_repeat:
                flash('Пароли не совпадают.', 'warning')
            else:
                crypt_status, crypted_pass = crypt_pass(password)
                if not crypt_status:
                    flash('Не удалось сменить пароль, возможно вы вводите недопустимые символы.', 'warning')
                else:
                    update_password_by_access_token(access_token, crypted_pass)
                    delete_recovers_by_user_id(r.data.id)
                    flash('Вы успешно сменили пароль.', 'success')
                    return redirect(url_for("view.landing"))
        except Exception as ex:
            logging.error(ex)

    return render_template("authentication/auth-reset-password.html")


# Уровень:              register
# База данных:          User
# HTML:                 auth-register
@view.route('/register/', methods=["GET", "POST"], defaults={'version': 1})
@view.route('/register/<version>', methods=["GET", "POST"])
def register(version):
    status, url = auto_redirect()
    if status:
        return redirect(url)
    if request.method == "POST":
        input_phone_number = normal_phone_number(request.form.get("phonenumber"))
        password = request.form.get("password")
        if check_user_by_phone(input_phone_number):
            # пользователь уже существует
            flash('Аккаунт с таким номером телефона уже существует!', 'warning')
        else:
            crypt_status, crypted_pass = crypt_pass(password)
            if crypt_status:
                inserted_user = add_user(input_phone_number, crypted_pass)
                flash('Ваш аккаунт появился в базе')
                try:
                    user_id = inserted_user.inserted_id
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
                except Exception as ex:
                    logging.error(ex)
                    flash('Зайдите еще раз и заполните анкету')
                return redirect("/login")
            else:
                flash('Не удалось зарегистрировать вас, возможно вы вводите недопустимый пароль!')
    if version == "2":
        return render_template("authentication/auth-register-2.html")
    else:
        return render_template("authentication/auth-register.html")


# Уровень:              registered
# База данных:          User
# HTML:                 registered
@view.route('/registered', methods=['POST', 'GET'])
@login_required
def registered():
    # auto redirect
    status, url = auto_redirect(ignore_role=Role.REGISTERED)
    if status:
        return redirect(url)
    # check session
    if not check_session():
        logout_user()
        return redirect(url_for("view.landing"))

    if request.method == "POST":
        try:
            # auto redirect
            status, url = auto_redirect(ignore_role=Role.REGISTERED)
            if status:
                return redirect(url)

            input_first_name = request.form.get("first_name")
            input_last_name = request.form.get("last_name")
            input_birthday = request.form.get("birthday")
            update_registered_user(current_user.id, first_name=input_first_name, last_name=input_last_name,
                                   birthday=input_birthday)

            if current_user.telegram_id is None:
                flash('Привяжите телеграмм аккаунт.', 'warning')
            else:
                flash('Ваш профиль изменен. Ожидайте подтверждения администрации.', 'success')
                notify_admins('Новый пользователь', url_for('admin.users_registered'), 'mdi mdi-head-plus', 'warning',
                              f'Новый пользователь подал заявку на регистрацию ID={current_user.id}')
                return redirect(url_for('view.landing'))

        except Exception as ex:
            logging.error(ex)
            return redirect(url_for('view.landing'))

        return redirect(url_for('view.registered'))

    return render_template("authentication/auth-registered.html")


# Уровень:              registered/token
# База данных:          User
# HTML:                 -
@view.route('/registered/token', methods=['POST'])
@login_required
def registered_token():
    try:
        if current_user.telegram_id is None:
            status, token = create_token()
            if status:
                update_user(current_user.id, 'access_token', token)
                return json.dumps({'icon': 'info', 'title': 'Telegram',
                                   'text': f'<ol><li>Скопируй код снизу</li><li>Отправь его нашему <a href="{system_variables["tg_bot"]}" target="_blank"> телеграмм боту </a></li>',
                                   'footer': f'<a onclick="clipboard(\'{token}\');">{token}</a>',
                                   'confirm_btn_text': f'<a href="{system_variables["tg_bot"]}" target="_blank" style="color: white"> Перейти к боту </a>'}), 200, {
                    'ContentType': 'application/json'}
            else:
                return json.dumps({'icon': 'warning', 'title': 'Telegram',
                                   'text': 'Не удалось создать токен для привязывания вашего аккаунта к телеграм боту.',
                                   'confirm_btn_text': 'OK'
                                   }), 200, {
                    'ContentType': 'application/json'}
        else:
            return json.dumps({'icon': 'success', 'title': 'Telegram',
                               'text': 'Ваш аккаунт уже привязан к телеграм боту.',
                               'confirm_btn_text': 'OK'
                               }), 200, {
                'ContentType': 'application/json'}
    except Exception as ex:
        return json.dumps({'icon': 'error', 'title': 'Ошибка',
                           'text': str(ex), 'confirm_btn_text': 'OK'
                           }), 200, {'ContentType': 'application/json'}


# secure

# Уровень:              account/password
# База данных:          User
# HTML:                 -
@view.route('/account/password', methods=['POST'])
@login_required
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
                               'text': 'Не удалось сменить пароль, возможно вы вводите недопустимые символы.',
                               }), 200, {
                'ContentType': 'application/json'}
        update_user(current_user.id, 'password', crypted_pass)
        return json.dumps({'icon': 'success', 'title': 'Смена пароля',
                           'text': 'Вы успешно сменили пароль.',
                           }), 200, {
            'ContentType': 'application/json'}
    except Exception as ex:
        logging.error(ex)
        return json.dumps({'icon': 'error', 'title': 'Ошибка',
                           'text': str(ex)
                           }), 200, {'ContentType': 'application/json'}


# Уровень:              account/telegram
# База данных:          User
# HTML:                 -
@view.route('/account/telegram', methods=['POST'])
@login_required
def get_telegram_token():
    try:
        if current_user.telegram_id is None:
            status, token = create_token()
            if status:
                update_user(current_user.id, 'access_token', token)
                return json.dumps({'success': True, 'token': token}), 200, {'ContentType': 'application/json'}
    except Exception as ex:
        logging.error(ex)
    return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}


# Уровень:              account/telegram/auth
# База данных:          User
# HTML:                 -
@view.route('/account/telegram/auth', methods=['POST'])
@login_required
def set_telegram_auth():
    try:
        if current_user.telegram_id is not None:
            status = request.form['status'] == "true"
            update_user(current_user.id, 'telegram_auth', status)
            return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    except Exception as ex:
        logging.error(ex)
    return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}


# Уровень:              faceid
# База данных:          User
# HTML:                 faceid
@view.route('/faceid', methods=['POST', 'GET'])
@login_required
def face_id():
    # check session
    if not check_session():
        logout_user()
        return redirect(url_for("view.landing"))

    return render_template("face_id.html")


# Уровень:              faceid/greeting
# База данных:          User
# HTML:                 -
@view.route('/faceid/greeting', methods=['POST'])
@login_required
def face_id_greeting():
    try:
        greeting = request.form.get("greeting")
        if len(TextFilter(greeting).find_bad_words()) > 0:
            return json.dumps(
                {'success': False, "info": "Запрещено использовать нецензурную лексику в приветствиях"}), 200, {
                'ContentType': 'application/json'}

        update_user(current_user.id, 'face_id.greeting', greeting)
        return json.dumps({'success': True,
                           "info": f"Приветствие изменено: '{greeting}, {current_user.first_name}!'"}), 200, {
            'ContentType': 'application/json'}
    except Exception as ex:
        return json.dumps({'success': False, "info": str(ex)}), 200, {'ContentType': 'application/json'}
