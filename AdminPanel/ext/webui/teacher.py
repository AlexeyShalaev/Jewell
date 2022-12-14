from flask import Blueprint

teacher = Blueprint('teacher', __name__, url_prefix='teacher', template_folder='templates')
