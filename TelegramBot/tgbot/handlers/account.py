from aiogram import types, Dispatcher

from TelegramBot.tgbot.misc.crypt import create_token
from TelegramBot.tgbot.services.MongoDB.users import get_user_by_telegram_id, update_auth_token

web_url = 'http://127.0.0.5:5000/login'


async def bot_account_login(message: types.Message):
    r = get_user_by_telegram_id(message.from_user.id)
    if r.success and r.data.telegram_auth:
        status, token = create_token()
        if status:
            update_auth_token(r.data.id, token)
            await message.answer(f'{web_url}/{token}')
        else:
            await message.answer(f"Не удалось создать ссылку для авторизации.\n {web_url}")
    else:
        await message.answer(
            f"Привяжите авторизацию через телеграмм бота на сайте для более быстрого входа.\n {web_url}")


async def bot_account_sessions(message: types.Message):
    # todo sessions
    await message.answer("Сессии")


def register_account(dp: Dispatcher):
    dp.register_message_handler(bot_account_login, text="Войти на сайт 📲", registered=True)
    dp.register_message_handler(bot_account_sessions, text="Сессии 🖥", registered=True)
