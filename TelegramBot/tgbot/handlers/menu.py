from aiogram import types, Dispatcher
from TelegramBot.tgbot import links
from TelegramBot.tgbot.keyboards import menu, account
from TelegramBot.tgbot.services.MongoDB.users import get_user_by_telegram_id, Role
from TelegramBot.tgbot.services.api import get_admin_attendance, get_student_attendance


async def bot_menu(message: types.Message):
    await message.answer("Выберите категорию", reply_markup=menu.categories)


async def bot_admin_menu(message: types.Message):
    await message.answer("Выберите категорию", reply_markup=menu.admin)


async def bot_menu_account(message: types.Message):
    await message.answer("Выберите нужный раздел", reply_markup=account.registered)


async def bot_menu_attendance(message: types.Message):
    r = get_user_by_telegram_id(message.from_user.id)
    if not r.success:
        await message.answer("Не удалось получить данные.")
    else:
        user = r.data
        if user.role == Role.ADMIN:
            status, data = get_admin_attendance()
            if not status:
                await message.answer("Сервер не вернул положительный результат.")
            else:
                msg = 'Список студентов, выбравших поездку, с плохой посещаемостью:\n\n'
                for i in data:
                    msg += f'[{i["name"]}]({i["href"]}): {i["visits"]}\n'
                await message.answer(msg, parse_mode=types.ParseMode.MARKDOWN)
        elif user.role == Role.STUDENT:
            status, data = get_student_attendance(str(user.id))
            if not status:
                await message.answer("Извините, произошла какая-то ошибка.")
            else:
                msg = f'[Анализ вашей посещаемости]({data["href"]})\n\n' \
                      f'Кол-во посещений:    *{data["visits_count"]}*/{data["visits_aim"]}\n' \
                      f'Проценты:                         *{data["percent"]}*%\n' \
                      f'Частота:                           *{data["frequency"]}*\n' \
                      f'\n{data["extra_info"]}'
                await message.answer(msg, parse_mode=types.ParseMode.MARKDOWN)
        else:
            await message.answer("Данная доступна только студентам.")


async def bot_menu_schedule(message: types.Message):
    await message.answer_photo(links.courses_image, f'[КУРСЫ ЯХАД JEWELL]({links.courses})',
                               parse_mode=types.ParseMode.MARKDOWN)


async def bot_menu_chat(message: types.Message):
    await message.answer(f"Переходите по [ссылке]({links.chat}) и общайся на разные темы со всеми участниками клуба!",
                         parse_mode=types.ParseMode.MARKDOWN)


def register_menu(dp: Dispatcher):
    dp.register_message_handler(bot_menu, commands=['menu', 'help', 'info', 'start'])
    dp.register_message_handler(bot_admin_menu, commands=['admin'], is_group=False, role='admin')
    dp.register_message_handler(bot_menu, text="Назад 🔙")
    dp.register_message_handler(bot_menu_attendance, text="Посещаемость ✅", registered=True)
    dp.register_message_handler(bot_menu_account, text="Аккаунт ⚙", registered=True, is_group=False)
    dp.register_message_handler(bot_menu_schedule, text="Расписание 📅")
    dp.register_message_handler(bot_menu_chat, text="Чат 💬")
