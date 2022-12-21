from AdminPanel.ext.logistics import *
from AdminPanel.ext.database.users import *
from AdminPanel.ext.database.recover_pw import *
from AdminPanel.ext.database.flask_sessions import *
from AdminPanel.ext.models.userModel import *
from AdminPanel.ext.models.recover_pw import *
from AdminPanel.ext.telegram_bot.message import *
from AdminPanel.ext.crypt import *
from flask import *
from flask_toastr import *
from flask_login import *
import logging
from random import choice

logger = logging.getLogger(__name__)  # logging
view = Blueprint('view', __name__, template_folder='templates', static_folder='assets')  # route


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
                    add_flask_session(id=session.get('_id'),
                                      user_id=session.get('_user_id'),
                                      user_agent=request.user_agent,
                                      fresh=session.get('_fresh'),
                                      ip=get_info_by_ip(request.remote_addr))
                    update_user(user.data.id, 'access_token', '')
                    flash('Вы успешно авторизовались!', 'success')
                    logger.info(f'авторизован пользователь {input_phone_number}')
                    if user.data.telegram_id is not None:
                        msg = f'Совершен вход в ваш аккаунт. (IP: {request.remote_addr})\n' \
                              'Если это не вы срочно смените пароль в настройках.'
                        # TODO: норм безопасность
                        send_message(msg, user.data.telegram_id)
                    return redirect(request.args.get("next") or url_for("view.login"))
                else:
                    flash('Неверный пароль!', 'warning')
        except Exception as ex:
            logger.error(ex)
    templates = ['auth-login.html', 'auth-login-2.html']  # для случайной генерации шаблона
    return render_template("custom/authentication/" + choice(templates))


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
            # авторизуем пользователя
            login_user(user.data)
            add_flask_session(id=session.get('_id'),
                              user_id=session.get('_user_id'),
                              user_agent=request.user_agent,
                              fresh=session.get('_fresh'),
                              ip=get_info_by_ip(request.remote_addr))
            flash('Вы успешно авторизовались!', 'success')
            update_user(user.data.id, 'access_token', '')
    except Exception as ex:
        logger.error(ex)
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
        return render_template("custom/authentication/" + choice(templates))
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
                    else:
                        status, token = create_token()
                        if status:
                            update_user(user.data.id, 'access_token', token)
                            recover_url = request.host_url + 'login/' + token
                            msg = f'Произошел запрос на восстановление доступа к аккаунту.\n' \
                                  f'Перейдите по ссылке и смените пароль.\n' \
                                  f'{recover_url}' \
                                  '\nЕсли это не вы срочно смените пароль в настройках.'
                            send_message(msg, user.data.telegram_id)
                            flash('Наш бот отправит вам ссылку на временный доступ к аккаунту!', 'success')
                        else:
                            flash('Не удалось отправить ссылку на восстановление пароля!', 'warning')
                return redirect("/login")
        except Exception as ex:
            logger.error(ex)
    if version == "2":
        return render_template("custom/authentication/auth-recoverpw-2.html")
    else:
        return render_template("custom/authentication/auth-recoverpw.html")


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
                add_user(input_phone_number, crypted_pass)
                flash('Вы успешно зарегистрированы')
                return redirect("/login")
            else:
                flash('Не удалось зарегистрировать вас, возможно вы вводите недопустимый пароль!')
    if version == "2":
        return render_template("custom/authentication/auth-register-2.html")
    else:
        return render_template("custom/authentication/auth-register.html")


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
            input_first_name = request.form.get("first_name")
            input_last_name = request.form.get("last_name")
            input_birthday = request.form.get("birthday")
            update_registered_user(current_user.id, first_name=input_first_name, last_name=input_last_name,
                                   birthday=input_birthday)
            flash('Ваш профиль изменен. Ожидайте подтверждения администрации.', 'success')
        except Exception as ex:
            logger.error(ex)
    return render_template("custom/authentication/registered.html",
                           telegram_validated=current_user.telegram_id is not None)


# Уровень:              registered/token
# База данных:          User
# HTML:                 -
@view.route('/registered/token', methods=['POST'])
def registered_token():
    try:
        if current_user.telegram_id is None:
            status, token = create_token()
            if status:
                update_user(current_user.id, 'access_token', token)
                return json.dumps({'icon': 'info', 'title': 'Telegram',
                                   'text': 'Отправьте данный токен нашему телеграмм боту и он привяжет ваш аккаунт.',
                                   'footer': f'<a href="https://t.me/yahad_alex_bot">{token}</a>'}), 200, {
                           'ContentType': 'application/json'}
            else:
                return json.dumps({'icon': 'warning', 'title': 'Telegram',
                                   'text': 'Не удалось создать токен для привязывания вашего аккаунта к телеграм боту.',
                                   }), 200, {
                           'ContentType': 'application/json'}
        else:
            return json.dumps({'icon': 'success', 'title': 'Telegram',
                               'text': 'Ваш аккаунт уже привязан к телеграм боту.',
                               }), 200, {
                       'ContentType': 'application/json'}
    except Exception as ex:
        return json.dumps({'icon': 'error', 'title': 'Ошибка',
                           'text': str(ex)
                           }), 200, {'ContentType': 'application/json'}


# secure

# Уровень:              sessions/logout/<id>
# База данных:          flask_sessions
# HTML:                 -
@view.route('/sessions/logout/<id>', methods=['POST'])
def sessions_logout(id):
    try:
        delete_flask_session(id)
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    except Exception as ex:
        logger.error(str(ex))
    return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}


# Miscellaneous routines

def normal_phone_number(phone_number: str) -> str:
    # функция возвращает номер телефона в формате 8XXXXXXXXXX
    phone_number = phone_number.replace('+7', '8', 1)
    if phone_number.startswith('7'):
        phone_number = phone_number.replace('7', '8', 1)
    return phone_number
