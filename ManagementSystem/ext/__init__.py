from ManagementSystem.config import load_config
from ManagementSystem.ext.configurator import SystemVariables

system_variables = SystemVariables()
config = load_config()  # config

telegram_chat = config.tg_bot.chat
