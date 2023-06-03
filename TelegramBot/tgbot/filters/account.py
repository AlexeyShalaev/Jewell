import typing

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from TelegramBot.tgbot import links
from TelegramBot.tgbot.services.MongoDB.users import check_user_by_telegram_id

reg_url = f'{links.jewell}/register'


class AccountFilter(BoundFilter):
    key = 'registered'

    def __init__(self, registered: typing.Optional[bool] = None):
        self.registered = registered

    async def check(self, obj):
        if self.registered is None:
            return False
        if not check_user_by_telegram_id(obj.from_user.id):
            await obj.reply(
                f"Вы не [зарегистрированы в системе]({reg_url}) или у вас не привязан телеграмм аккаунт в настройках.",
                parse_mode=types.ParseMode.MARKDOWN)
            return False
        return True
