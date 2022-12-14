from werkzeug.security import generate_password_hash, check_password_hash
import logging

logger = logging.getLogger(__name__)  # logging


# функция создает хеш-сумму, которая будет храниться в базе данных
def crypt_pass(password: str) -> (bool, str):
    try:
        return True, generate_password_hash(password)
    except Exception as ex:
        logger.error(ex)
        return False, str(ex)


# функция проверяет хеш из базы данных и введенный пароль
def check_pass(self, hashed_pass: str, input_pass: str) -> bool:
    try:
        return check_password_hash(hashed_pass, input_pass)
    except Exception as ex:
        logger.error(ex)
        return False
