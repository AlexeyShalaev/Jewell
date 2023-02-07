from aiogram import types, Dispatcher

from TelegramBot.tgbot import links
from TelegramBot.tgbot.keyboards.sessions import create_keyboard
from TelegramBot.tgbot.misc.crypt import create_token
from TelegramBot.tgbot.services.MongoDB.flask_sessions import get_flask_sessions_by_user_id
from TelegramBot.tgbot.services.MongoDB.users import get_user_by_telegram_id, update_auth_token

login_url = f'{links.jewell}/login'


async def bot_account_login(message: types.Message):
    r = get_user_by_telegram_id(message.from_user.id)
    if r.success and r.data.telegram_auth:
        status, token = create_token()
        if status:
            update_auth_token(r.data.id, token)
            await message.answer(f'[Вход]({login_url}/{token})', parse_mode=types.ParseMode.MARKDOWN)
        else:
            await message.answer(f"[Не удалось создать ссылку для авторизации]({login_url})",
                                 parse_mode=types.ParseMode.MARKDOWN)
    else:
        await message.answer(
            f"Привяжите авторизацию через телеграмм бота на сайте для более быстрого [входа]({login_url})",
            parse_mode=types.ParseMode.MARKDOWN)


async def bot_account_sessions(message: types.Message):
    user = get_user_by_telegram_id(message.from_user.id).data
    sessions = get_flask_sessions_by_user_id(user.id).data
    if len(sessions) == 0:
        await message.answer("У вас нет активных сессий!")
    else:
        keyboard = create_keyboard(sessions)
        await message.answer("Выберите сессию, которую хотите завершить", reply_markup=keyboard)


def register_account(dp: Dispatcher):
    dp.register_message_handler(bot_account_login, text="Войти на сайт 📲", registered=True, is_group=False)
    dp.register_message_handler(bot_account_sessions, text="Сессии 🖥", registered=True, is_group=False)
