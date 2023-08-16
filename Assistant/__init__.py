import logging

from Assistant.config import load_config

logging.basicConfig(
    filename='assistant.log',
    format="%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
    datefmt='%d.%m.%Y %H:%M:%S',
    level=logging.INFO,
)

config = load_config()  # config

jewell_token = config.api.jewell

links = config.links
