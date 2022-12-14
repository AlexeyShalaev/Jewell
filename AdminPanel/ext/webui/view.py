from flask import *
from flask_toastr import *
from flask_login import *
from AdminPanel.ext.models.jewell import *
from AdminPanel.ext.crypt import *
from AdminPanel.ext.database.UserLogin import UserLogin
import logging
from random import choice

view = Blueprint('view', __name__, template_folder='templates', static_folder='assets')  # route
logger = logging.getLogger(__name__)  # logging


# Уровень:              Главная страница
# База данных:          -
# HTML:                 landing
@view.route('/')
def landing():
    if current_user.is_authenticated:
        if current_user.user.role == Role.STUDENT:
            return redirect("/student/home")
        elif current_user.user.role == Role.TEACHER:
            return redirect("/teacher/home")
        elif current_user.user.role == Role.ADMIN:
            return redirect("/admin/home")
    else:
        return render_template("landing.html")


# Accounting


# Уровень:              login
# База данных:          User
# HTML:                 auth-login
@view.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.user.role == Role.STUDENT:
            return redirect("/student/home")
        elif current_user.user.role == Role.TEACHER:
            return redirect("/teacher/home")
        elif current_user.user.role == Role.ADMIN:
            return redirect("/admin/home")
    else:
        if request.method == "POST":
            try:
                input_phone_number = request.form.get("phonenumber")
                input_password = request.form.get("password")
                user = User.find_one(User.phone_number == input_phone_number).run()
                if user is None:
                    flash('Пользователь не найден!', 'warning')
                else:
                    if check_password_hash(user.password, input_password):
                        # авторизуем пользователя
                        user_login = UserLogin().create(user)
                        login_user(user_login)
                        flash('Вы успешно авторизовались!', 'success')
                        logger.info(f'авторизован пользователь {input_phone_number}')
                        return redirect(request.args.get("next") or url_for("landing"))
                    else:
                        flash('Неверный пароль!', 'warning')
            except Exception as ex:
                logger.error(ex)
        templates = ['auth-login.html', 'auth-login-2.html']  # для случайной генерации шаблона
        return render_template("custom/authentication/" + choice(templates))


# Уровень:              recoverpw
# База данных:          User
# HTML:                 auth-recoverpw
@view.route('/recoverpw/', methods=["GET", "POST"], defaults={'version': 1})
@view.route('/recoverpw/<version>', methods=["GET", "POST"])
def recoverpw(version):
    if current_user.is_authenticated:
        if current_user.user.role == Role.STUDENT:
            return redirect("/student/home")
        elif current_user.user.role == Role.TEACHER:
            return redirect("/teacher/home")
        elif current_user.user.role == Role.ADMIN:
            return redirect("/admin/home")
    else:
        if request.method == "POST":
            phone_number = request.form.get("phonenumber")
            # TODO: recoverpw
            return phone_number
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
    if current_user.is_authenticated:
        if current_user.user.role == Role.STUDENT:
            return redirect("/student/home")
        elif current_user.user.role == Role.TEACHER:
            return redirect("/teacher/home")
        elif current_user.user.role == Role.ADMIN:
            return redirect("/admin/home")
    else:
        if request.method == "POST":
            fullname = request.form.get("fullname")
            phone_number = request.form.get("phonenumber")
            password = request.form.get("password")
            # TODO: register
            return fullname + " " + phone_number + " " + password
        if version == "2":
            return render_template("custom/authentication/auth-register-2.html")
        else:
            return render_template("custom/authentication/auth-register.html")
