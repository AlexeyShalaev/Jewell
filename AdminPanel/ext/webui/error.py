from flask import *
from flask_toastr import *
from flask_login import *
from AdminPanel.ext.models.jewell import Role
import logging

error = Blueprint('error', __name__, template_folder='templates/custom/errors', static_folder='assets')  # route
logger = logging.getLogger(__name__)  # logging


@error.app_errorhandler(404)
def pageNotFound(e):
    if current_user.is_authenticated:
        if current_user.user.role == Role.STUDENT:
            return redirect("/student/home")
        elif current_user.user.role == Role.TEACHER:
            return redirect("/teacher/home")
        elif current_user.user.role == Role.ADMIN:
            return redirect("/admin/home")
    else:
        return render_template("error-404.html")


@error.app_errorhandler(500)
def error500(e):
    if current_user.is_authenticated:
        if current_user.user.role == Role.STUDENT:
            return redirect("/student/home")
        elif current_user.user.role == Role.TEACHER:
            return redirect("/teacher/home")
        elif current_user.user.role == Role.ADMIN:
            return redirect("/admin/home")
    else:
        return render_template("error-500.html")
