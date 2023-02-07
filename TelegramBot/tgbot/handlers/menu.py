from aiogram import types, Dispatcher
from TelegramBot.tgbot import chat
from TelegramBot.tgbot.keyboards import menu, account
from TelegramBot.tgbot.services.MongoDB.users import get_user_by_telegram_id, Role


async def bot_menu(message: types.Message):
    await message.answer("Выберите категорию", reply_markup=menu.categories)


async def bot_menu_account(message: types.Message):
    await message.answer("Выберите нужный раздел", reply_markup=account.registered)


async def bot_menu_attendance(message: types.Message):
    r = get_user_by_telegram_id(message.from_user.id)
    if not r.success:
        await message.answer("Не удалось получить данные.")
    else:
        user = r.data
        if user.role == Role.ADMIN:
            # todo print some stat about attendance
            pass
        elif user.role == Role.STUDENT:
            # todo print attendance
            pass
        else:
            await message.answer("Данная команда не доступна.")


async def bot_menu_schedule(message: types.Message):
    # todo
    await message.answer("Расписание")


async def bot_menu_chat(message: types.Message):
    await message.answer(f"Переходите по [ссылке]({chat}) и общайся на разные темы со всеми участниками клуба!",
                         parse_mode=types.ParseMode.MARKDOWN)


def register_menu(dp: Dispatcher):
    dp.register_message_handler(bot_menu, commands=['menu', 'help', 'info', 'start'])
    dp.register_message_handler(bot_menu, text="Назад 🔙")
    dp.register_message_handler(bot_menu_attendance, text="Посещаемость ✅", registered=True)
    dp.register_message_handler(bot_menu_account, text="Аккаунт ⚙", registered=True)
    dp.register_message_handler(bot_menu_schedule, text="Расписание 📅")
    dp.register_message_handler(bot_menu_chat, text="Чат 💬")
