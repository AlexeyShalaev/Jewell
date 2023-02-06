import typing
from aiogram.dispatcher.filters import BoundFilter


class GroupFilter(BoundFilter):
    key = 'is_group'

    def __init__(self, is_group: typing.Optional[bool] = None):
        self.is_group = is_group

    async def check(self, obj):
        if self.is_group is None:
            return False
        chat_id = obj.chat.id
        if (chat_id >= 0) and self.is_group:
            await obj.reply("Команду можно использовать только в групповых чатах!")
            return False
        elif (chat_id <= 0) and not self.is_group:
            await obj.reply("Команду можно использовать только в личных чатах!")
            return False
        else:
            return True
