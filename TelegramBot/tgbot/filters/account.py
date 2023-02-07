import typing

from aiogram.dispatcher.filters import BoundFilter

from TelegramBot.tgbot.services.MongoDB.users import get_user_by_telegram_id, check_user_by_telegram_id


class AccountFilter(BoundFilter):
    key = 'registered'

    def __init__(self, registered: typing.Optional[bool] = None):
        self.registered = registered

    async def check(self, obj):
        if self.registered is None:
            return False
        if not check_user_by_telegram_id(obj.from_user.id):
            await obj.reply("Вы не зарегистрированы в системе или у вас не привязан телеграмм аккаунт в настройках. http://103.57.251.140:5000/register/")
            return False
        return True
