from ManagementSystem.config import load_config

config = load_config()  # config

url = f'https://api.telegram.org/bot{config.tg_bot.token}/'
