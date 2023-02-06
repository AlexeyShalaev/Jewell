from aiogram import Dispatcher

from .environment import EnvironmentMiddleware


def register_middlewares(dp: Dispatcher):
    dp.middleware.setup(EnvironmentMiddleware())
