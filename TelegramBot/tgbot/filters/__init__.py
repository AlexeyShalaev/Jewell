from aiogram import Dispatcher

from TelegramBot.tgbot.filters.account import AccountFilter
from TelegramBot.tgbot.filters.role import RoleFilter
from TelegramBot.tgbot.filters.group import GroupFilter


def register_filters(dp: Dispatcher):
    dp.filters_factory.bind(AccountFilter)
    dp.filters_factory.bind(RoleFilter)
    dp.filters_factory.bind(GroupFilter)
