import logging
from secrets import token_hex


def create_token(n_bytes: int = 16) -> (bool, str):
    try:
        return True, token_hex(n_bytes)
    except Exception as ex:
        logging.error(ex)
        return False, str(ex)
