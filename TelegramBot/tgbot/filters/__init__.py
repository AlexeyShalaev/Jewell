from aiogram import Dispatcher

from TelegramBot.tgbot.filters.admin import AdminFilter
from TelegramBot.tgbot.filters.group import GroupFilter


def register_filters(dp: Dispatcher):
    dp.filters_factory.bind(AdminFilter)
    dp.filters_factory.bind(GroupFilter)
