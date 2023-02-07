from aiogram import Dispatcher

from TelegramBot.tgbot.handlers.account import register_account
from TelegramBot.tgbot.handlers.admin import register_admin
from TelegramBot.tgbot.handlers.menu import register_menu


def register_handlers(dp: Dispatcher):
    register_account(dp)
    register_admin(dp)
    register_menu(dp)
