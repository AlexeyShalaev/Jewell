from flask import Blueprint, send_file
import os
import logging

logger = logging.getLogger(__name__)  # logging
api = Blueprint('api', __name__, url_prefix='/api', template_folder='templates', static_folder='assets')


# Уровень:              account/avatar/user_id
# База данных:          storage/avatars
# HTML:                 -
@api.route('/avatar/<user_id>', methods=['POST', 'GET'])
def get_avatar(user_id):
    filename = 'undraw_avatar.jpg'
    directory = 'storage/avatars/'
    try:
        files = os.listdir(directory)
        for file in files:
            if user_id == file.split('.')[0]:
                filename = file
                break
    except Exception as ex:
        logger.error(ex)
    return send_file(directory + filename, as_attachment=True)
