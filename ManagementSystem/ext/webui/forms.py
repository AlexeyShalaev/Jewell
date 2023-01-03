from logging import getLogger

from flask import *

logger = getLogger(__name__)  # logging
forms = Blueprint('forms', __name__, url_prefix='/forms', template_folder='templates', static_folder='assets')
