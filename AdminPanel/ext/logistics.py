from AdminPanel.ext.database.users import *
from AdminPanel.ext.database.flask_sessions import *
from flask import *
from flask_login import *


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


def check_session():
    # если сессии нет в БД -> данную сессию необходимо закрыть
    if current_user.is_authenticated:
        flask_session = get_flask_session_by_id(session.get('_id', current_user.id))
        return flask_session.success
    return True
