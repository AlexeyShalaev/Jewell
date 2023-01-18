from logging import getLogger

from flask import *
from flask_login import *
from flask_toastr import *

from ManagementSystem.ext.database.users import *
from ManagementSystem.ext.webui.admin import admin
from ManagementSystem.ext.webui.api import api
from ManagementSystem.ext.webui.error import error
from ManagementSystem.ext.webui.networking import networking
from ManagementSystem.ext.webui.forms import forms
from ManagementSystem.ext.webui.other import other
from ManagementSystem.ext.webui.student import student
from ManagementSystem.ext.webui.teacher import teacher
from ManagementSystem.ext.webui.view import view
from ManagementSystem.ext import system_variables
from config import load_config

config = load_config()  # config
logger = getLogger(__name__)  # logging

# flask
app = Flask(config.flask.app_name)
app.register_blueprint(view)
app.register_blueprint(error)
app.register_blueprint(api)
app.register_blueprint(networking)
app.register_blueprint(forms)
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


def main():
    logger.info("Starting app")
    app.run(debug=True, host='0.0.0.0')


if __name__ == "__main__":
    main()
