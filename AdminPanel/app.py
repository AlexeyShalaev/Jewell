# Flask imports
from flask import Flask, render_template
from flask_login import LoginManager
from flask_toastr import Toastr

from AdminPanel.ext.webui.view import view
from AdminPanel.ext.webui.api import api
from AdminPanel.ext.webui.student import student
from AdminPanel.ext.webui.teacher import teacher
from AdminPanel.ext.webui.admin import admin
from AdminPanel.ext.database.UserLogin import UserLogin

import logging
from config import load_config

config = load_config()  # config
logger = logging.getLogger(__name__)  # logging

# flask
app = Flask(config.flask.app_name)
app.register_blueprint(view)
app.register_blueprint(api)
app.register_blueprint(student)
app.register_blueprint(teacher)
app.register_blueprint(admin)
app.config['SECRET_KEY'] = config.flask.secret_key

toastr = Toastr(app)

login_manager = LoginManager(app)
login_manager.login_view = config.flask.login_manager["login_view"]
login_manager.login_message = config.flask.login_manager["login_message"]
login_manager.login_message_category = config.flask.login_manager["login_message_category"]


@login_manager.user_loader
def load_user(phone_number):
    user = UserLogin().fromDB(phone_number)
    if user:
        return user


def main():
    logger.info("Starting app")
    app.run(debug=True, host='0.0.0.0')


if __name__ == "__main__":
    main()
