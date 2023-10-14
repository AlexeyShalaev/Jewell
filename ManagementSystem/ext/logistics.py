from functools import wraps
from flask import session, redirect, url_for, request
from flask_login import current_user

from ManagementSystem.ext.database.flask_sessions import get_flask_session_by_id
from ManagementSystem.ext.database.users import Role


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


def auto_render():
    if current_user.is_authenticated:
        if current_user.role == Role.REGISTERED:
            return False, "error-500.html"
        elif current_user.role == Role.STUDENT:
            return True, "/student"
        elif current_user.role == Role.TEACHER:
            return True, "/teacher"
        elif current_user.role == Role.ADMIN:
            return True, "/admin"
    return False, "error-500.html"


def check_session():
    # если сессии нет в БД -> данную сессию необходимо закрыть
    if current_user.is_authenticated:
        flask_session = get_flask_session_by_id(session.get('_id', current_user.id))
        return flask_session.success
    return True


def login_required_next(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            # Сохраняем исходный URL в сессии
            session['next_url'] = request.url
            return redirect(url_for('view.login'))
        return func(*args, **kwargs)
    return decorated_function