import logging
from secrets import token_hex

import cryptocode
from werkzeug.security import generate_password_hash, check_password_hash


# функция создает хеш-сумму, которая будет храниться в базе данных
def crypt_pass(password: str) -> (bool, str):
    try:
        return True, generate_password_hash(password)
    except Exception as ex:
        logging.error(ex)
        return False, str(ex)


# функция проверяет хеш из базы данных и введенный пароль
def check_pass(hashed_pass: str, input_pass: str) -> bool:
    try:
        return check_password_hash(hashed_pass, input_pass)
    except Exception as ex:
        logging.error(ex)
        return False


def create_token(n_bytes: int = 16) -> (bool, str):
    try:
        return True, token_hex(n_bytes)
    except Exception as ex:
        logging.error(ex)
        return False, str(ex)


def encrypt_id_with_no_digits(code: str) -> (bool, str):
    try:
        result = ''
        for symbol in code:
            if symbol.isdigit():
                result += chr(65 + int(symbol))
            else:
                result += symbol
        return True, result
    except Exception as ex:
        logging.error(ex)
        return False, ''


def decrypt_id_with_no_digits(code: str) -> (bool, str):
    try:
        result = ''
        for symbol in code:
            if symbol.isupper():
                result += str(ord(symbol) - 65)
            else:
                result += symbol
        return True, result
    except Exception as ex:
        logging.error(ex)
        return False, str(ex)


def encode_word(word: str, password: str) -> (bool, str):
    try:
        return True, cryptocode.encrypt(word, password)
    except:
        return False, None


def decode_word(word: str, password: str) -> str:
    try:
        return cryptocode.decrypt(word, password)
    except:
        return ''
