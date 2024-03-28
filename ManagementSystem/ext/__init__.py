import os

from ManagementSystem.config import load_config
from ManagementSystem.ext.configurator import SystemVariables

system_variables = SystemVariables()
config = load_config()  # config

api_token = config.flask.api_token

telegram_chat = config.tg_bot.chat

directories = {
    'avatars': 'storage/database/avatars',
    'games': 'storage/database/games',
    'products': 'storage/database/products',
    'records': 'storage/database/records',
    'animations': 'storage/database/animations',
}

for directory in directories.values():
    os.makedirs(directory, exist_ok=True)

valid_images = ['jpeg', 'jpg', 'png', 'heic']
