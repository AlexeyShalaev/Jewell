from AdminPanel.ext.models.userModel import *
from AdminPanel.ext.database.users import *
from AdminPanel.ext.database.recover_pw import *
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
