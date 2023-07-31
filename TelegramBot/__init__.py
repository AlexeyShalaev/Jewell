import logging

logging.basicConfig(
    filename='bot.log',
    format="%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
    datefmt='%H:%M:%S',
    level=logging.INFO,
)