from flask import Blueprint, send_file
from AdminPanel.ext.crypt import *
import os
import logging

logger = logging.getLogger(__name__)  # logging
api = Blueprint('api', __name__, url_prefix='/api', template_folder='templates', static_folder='assets')


# Уровень:              avatar/user_id
# База данных:          storage/avatars
# HTML:                 -
@api.route('/avatar/<user_id>', methods=['POST', 'GET'])
def get_avatar(user_id):
    filename = 'undraw_avatar.jpg'
    directory = 'storage/avatars/'
    resp_status, data = encrypt_id_with_no_digits(str(user_id))
    if resp_status:
        try:
            files = os.listdir(directory)
            for file in files:
                if data == file.split('.')[0]:
                    filename = file
                    break
        except Exception as ex:
            logger.error(ex)
    return send_file(directory + filename, as_attachment=True)
