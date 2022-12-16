from AdminPanel.ext.models.userModel import *
from AdminPanel.ext.database.users import *
from AdminPanel.ext.database.recover_pw import *
from AdminPanel.ext.models.recover_pw import *
from flask import *
from flask_toastr import *
from flask_login import *
from AdminPanel.ext.crypt import *
import logging
from random import choice

view = Blueprint('view', __name__, template_folder='templates', static_folder='assets')  # route
logger = logging.getLogger(__name__)  # logging


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
                    flash('Вы успешно авторизовались!', 'success')
                    logger.info(f'авторизован пользователь {input_phone_number}')
                    return redirect(request.args.get("next") or url_for("view.login"))
                else:
                    flash('Неверный пароль!', 'warning')
        except Exception as ex:
            logger.error(ex)
    templates = ['auth-login.html', 'auth-login-2.html']  # для случайной генерации шаблона
    return render_template("custom/authentication/" + choice(templates))


# Уровень:              logout
# База данных:          -
# HTML:                 auth-logout
@view.route('/logout')
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    templates = ['auth-logout.html', 'auth-logout-2.html']  # для случайной генерации шаблона
    return render_template("custom/authentication/" + choice(templates))


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
                add_recover(input_phone_number, user.data.id, user.data.telegram_id)
                if user.data.telegram_id is None:
                    flash('Ваш запрос передан администрации на рассмотрение!', 'info')
                else:
                    flash('Наш бот отправит вам в телеграмме новый пароль!', 'info')
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


# Registered
@view.route('/registered', methods=['POST', 'GET'])
@login_required
def registered():
    status, url = auto_redirect(ignore_role=Role.REGISTERED)
    if status:
        return redirect(url)
    if request.method == "POST":
        try:
            pass
        except Exception as ex:
            logger.error(ex)
    return render_template("custom/authentication/registered.html")


def normal_phone_number(phone_number: str) -> str:
    # функция возвращает номер телефона в формате 8XXXXXXXXXX
    phone_number = phone_number.replace('+7', '8', 1)
    if phone_number.startswith('7'):
        phone_number = phone_number.replace('7', '8', 1)
    return phone_number
