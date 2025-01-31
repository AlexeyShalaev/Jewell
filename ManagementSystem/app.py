import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from flask import *
from flask_login import *
from flask_toastr import *

from ext.database.flask_sessions import delete_flask_session, get_flask_session_by_id
from ext.database.users import *
from ext.webui.admin import admin
from ext.webui.api import api
from ext.webui.error import error
from ext.webui.networking import networking
from ext.webui.forms import forms
from ext.webui.games import games
from ext.webui.other import other
from ext.webui.student import student
from ext.webui.teacher import teacher
from ext.webui.view import view
from ext import system_variables
from config import load_config

config = load_config()  # config

# flask
app = Flask(config.flask.app_name)
app.register_blueprint(view)
app.register_blueprint(error)
app.register_blueprint(api)
app.register_blueprint(networking)
app.register_blueprint(forms)
app.register_blueprint(games)
app.register_blueprint(other)
app.register_blueprint(student)
app.register_blueprint(teacher)
app.register_blueprint(admin)
app.config['SECRET_KEY'] = config.flask.secret_key

app.jinja_env.globals['system_variables'] = system_variables

toastr = Toastr(app)

login_manager = LoginManager(app)
login_manager.login_view = config.flask.login_manager["login_view"]
login_manager.login_message = config.flask.login_manager["login_message"]
login_manager.login_message_category = config.flask.login_manager["login_message_category"]


# https://gist.github.com/leongjinqwen/a205cbe8185d8c83f9d300cc6c8634f1
@login_manager.user_loader
def load_user(id):
    user = get_user_by_id(id)
    if user.success:
        return user.data


@app.before_request
def before_request():
    # Получите идентификатор сессии из куки, если он существует
    session_id = request.cookies.get('session_id', None)
    if not current_user.is_authenticated and session_id is not None:
        resp = get_flask_session_by_id(session_id)
        if resp.success:
            flask_session = resp.data
            if flask_session.user_agent != str(request.user_agent) or flask_session.ip['query'] != request.remote_addr:
                # Если user_agent или ip не совпадают, то сессия устарела
                delete_flask_session(session_id)
            else:
                r = get_user_by_id(flask_session.user_id)
                if r.success:
                    login_user(r.data)


def main():
    logging.info("Starting app")
    app.run(host='0.0.0.0')


if __name__ == "__main__":
    main()
