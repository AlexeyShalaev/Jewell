from flask import *
from flask_toastr import *
from flask_login import *
from AdminPanel.ext.models.jewell import Role
import logging

view = Blueprint('view', __name__, template_folder='templates', static_folder='assets')  # route
logger = logging.getLogger(__name__)  # logging


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


@view.route('/login')
def login():
    if current_user.is_authenticated:
        if current_user.user.role == Role.STUDENT:
            return redirect("/student/home")
        elif current_user.user.role == Role.TEACHER:
            return redirect("/teacher/home")
        elif current_user.user.role == Role.ADMIN:
            return redirect("/admin/home")
    else:
        return render_template("custom/authentication/auth-login-2.html")
