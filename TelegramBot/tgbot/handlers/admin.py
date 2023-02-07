from aiogram import types, Dispatcher

from TelegramBot.tgbot.keyboards.snapshots import create_backups_keyboard
from TelegramBot.tgbot.misc.terminal import restart_website
from TelegramBot.tgbot.services.api import snapshot_dump, snapshot_backups


async def bot_admin_reload_website(message: types.Message):
    try:
        restart_website()
        await message.answer("Сайт перезагружен")
    except Exception as ex:
        await message.answer(f'Ошибка: {ex}')


async def bot_admin_dump(message: types.Message):
    status = snapshot_dump(message.chat.id)
    if status:
        await message.answer("Резервная копия создана")
    else:
        await message.answer("Не удалось создать резервную копию")


async def bot_admin_backups(message: types.Message):
    status, files = snapshot_backups()
    if not status:
        await message.answer("Не удалось получить список резервных копий.")
    elif len(files) == 0:
        await message.answer("На данный момент нет резервных копий.")
    else:
        files.reverse()
        keyboard = create_backups_keyboard(files)
        await message.answer("Выберите резервную копию, которую хотите восстановить", reply_markup=keyboard)


def register_admin(dp: Dispatcher):
    dp.register_message_handler(bot_admin_reload_website, text="Перезапустить сайт 🔃", is_group=False, role='admin')
    dp.register_message_handler(bot_admin_dump, text="Создать резервную копию 💽️", is_group=False, role='admin')
    dp.register_message_handler(bot_admin_backups, text="Восстановить из резервной копии 🗃", is_group=False,
                                role='admin')
