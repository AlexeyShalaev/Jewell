import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Regexp

from TelegramBot.tgbot.keyboards import menu
from TelegramBot.tgbot.keyboards.snapshots import create_backups_keyboard
from TelegramBot.tgbot.misc.terminal import restart_website
from TelegramBot.tgbot.services.api import snapshot_dump, snapshot_backups, stars_export_attendance


async def bot_admin_reload_website(message: types.Message):
    try:
        restart_website()
        await message.answer("Сайт перезагружен")
    except Exception as ex:
        logging.error(ex)
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


async def bot_admin_stars_export_month_choose_month(message: types.Message):
    await message.answer("Выберите месяц", reply_markup=menu.stars_month)


async def bot_admin_stars_export_month(message: types.Message):
    month = message.text.split(': ')[1]
    months = {
        "сентябрь": 9,
        "октябрь": 10,
        "ноябрь": 11,
        "декабрь": 12,
        "январь": 1,
        "февраль": 2,
        "март": 3,
        "апрель": 4,
        "май": 5,
        "июнь": 6
    }
    chosen_month = months.get(month)
    if chosen_month is None:
        await message.answer("Выберите месяц", reply_markup=menu.stars_month)
    else:
        status, info = stars_export_attendance(chosen_month)
        await message.answer(f"Экспорт посещаемости за месяц {month} завершен.\n\n[{status}]\n{info}")


def register_admin(dp: Dispatcher):
    dp.register_message_handler(bot_admin_reload_website, text="Перезапустить сайт 🔃", is_group=False, role='admin')
    dp.register_message_handler(bot_admin_dump, text="Создать резервную копию 💽️", is_group=False, role='admin')
    dp.register_message_handler(bot_admin_backups, text="Восстановить из резервной копии 🗃", is_group=False,
                                role='admin')
    dp.register_message_handler(bot_admin_stars_export_month_choose_month, text="Эскпорт посещаемости в Stars", is_group=False,
                                role='admin')
    dp.register_message_handler(
        bot_admin_stars_export_month,
        Regexp(r"^Stars: [а-яА-ЯёЁ]+$"),
        is_group=False,
        role='admin'
    )
