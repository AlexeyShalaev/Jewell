import logging
from secrets import token_hex

logger = logging.getLogger(__name__)  # logging


def create_token(n_bytes: int = 16) -> (bool, str):
    try:
        return True, token_hex(n_bytes)
    except Exception as ex:
        logger.error(ex)
        return False, str(ex)
