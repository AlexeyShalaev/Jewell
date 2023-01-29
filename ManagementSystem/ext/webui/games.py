import random
from logging import getLogger

from flask import *
from flask_login import login_required, logout_user, current_user

from ManagementSystem.ext.crypt import decode_word, encode_word
from ManagementSystem.ext.database.users import update_user, get_users, get_user_by_id
from ManagementSystem.ext.logistics import check_session

logger = getLogger(__name__)  # logging
games = Blueprint('games', __name__, url_prefix='/games', template_folder='templates/games', static_folder='assets')
game_5letters_path = 'storage/games/5letters/rus2129.txt'


# Уровень:              games/rating
# База данных:          Users
# HTML:                 -
@games.route('/rating', methods=['POST'])
def games_rating():
    top = []
    try:
        user_id = request.form['user_id']
        top_limit = int(request.form['top_limit'])
        users = get_users().data
        users.sort(key=lambda user: user.points, reverse=True)
        user_in_top = False
        for number, user in enumerate(users):
            if number + 1 > top_limit and user_in_top:
                break
            info = user.to_game_rating()
            info['number'] = number + 1
            if user_id == str(user.id):
                user_in_top = True
                top.append(info)
            elif number + 1 <= top_limit:
                top.append(info)
    except Exception as ex:
        logger.error(f'games_rating: {ex}')
    return json.dumps({'top': top}), 200, {'ContentType': 'application/json'}


# Уровень:              games/5letters
# База данных:          -
# HTML:                 5letters
@games.route('/5letters', methods=['POST', 'GET'])
@login_required
def five_letters():
    # check session
    if not check_session():
        logout_user()
        return redirect(url_for("view.landing"))

    try:
        words = []
        with open(game_5letters_path, encoding='utf-8') as file:
            words = [x[:5].upper() for x in file.readlines()]
        word = random.choice(words)
        encrypt_status, encrypted_word = encode_word(word, str(current_user.id))
        if encrypt_status and len(word) == 5:
            return render_template("5letters.html", encrypted_word=encrypted_word)

    except Exception as ex:
        logger.error(f'5letters_check: {ex}')
    return render_template("error-500.html")


# Уровень:              games/5letters/check
# База данных:          Users
# HTML:                 -
@games.route('/5letters/check', methods=['POST'])
def five_letters_check():
    extra = ''
    try:
        word = request.form['word'].upper()
        code = request.form['code']
        user_id = request.form['user_id']
        words = []
        with open(game_5letters_path, encoding='utf-8') as file:
            words = [x[:5].upper() for x in file.readlines()]
        riddle = decode_word(code, user_id)
        if riddle == word:
            status = 'win'
            points = 0
            r = get_user_by_id(user_id)
            if r.success:
                points = random.randint(25, 50)
                update_user(user_id, 'points', r.data.points + points)
            extra = str(points)
        else:
            if word in words:
                status = 'incorrect'
                extra = ''
                for index, letter in enumerate(word):
                    if letter not in riddle:
                        extra += '-'
                    else:
                        if letter == riddle[index]:
                            extra += '+'
                        else:
                            extra += '0'
            else:
                status = 'not_found'
    except Exception as ex:
        status = 'error'
        logger.error(f'5letters_check: {ex}')
    return json.dumps({'status': status, 'extra': extra}), 200, {'ContentType': 'application/json'}


# Уровень:              games/5letters/decode
# База данных:          -
# HTML:                 -
@games.route('/5letters/decode', methods=['POST'])
def five_letters_decode():
    code = request.form['code']
    user_id = request.form['user_id']
    riddle = decode_word(code, user_id)
    return json.dumps({'riddle': riddle}), 200, {'ContentType': 'application/json'}
