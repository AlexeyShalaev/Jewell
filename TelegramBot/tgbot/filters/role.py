import typing

from aiogram.dispatcher.filters import BoundFilter

from TelegramBot.tgbot.services.MongoDB.users import get_user_by_telegram_id


class RoleFilter(BoundFilter):
    key = 'role'

    def __init__(self, role: typing.Optional[str] = None):
        self.role = role

    async def check(self, obj):
        if self.role is None:
            return False
        r = get_user_by_telegram_id(obj.from_user.id)
        if not r.success:
            return False
        return r.data.role.value == self.role
