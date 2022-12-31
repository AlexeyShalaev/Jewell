from flask import *
from flask_toastr import *
from flask_login import *
from ManagementSystem.ext.models.userModel import *
import logging

error = Blueprint('error', __name__, template_folder='templates/errors', static_folder='assets')  # route


@error.app_errorhandler(404)
def pageNotFound(e):
    if current_user.is_authenticated:
        if current_user.role == Role.STUDENT:
            return redirect("/student/home")
        elif current_user.role == Role.TEACHER:
            return redirect("/teacher/home")
        elif current_user.role == Role.ADMIN:
            return redirect("/admin/home")
    else:
        return render_template("error-404.html")


@error.app_errorhandler(500)
def error500(e):
    if current_user.is_authenticated:
        if current_user.role == Role.STUDENT:
            return redirect("/student/home")
        elif current_user.role == Role.TEACHER:
            return redirect("/teacher/home")
        elif current_user.role == Role.ADMIN:
            return redirect("/admin/home")
    else:
        return render_template("error-500.html")
