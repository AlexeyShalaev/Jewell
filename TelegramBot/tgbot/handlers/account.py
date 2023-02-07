from aiogram import types, Dispatcher

from TelegramBot.tgbot import website
from TelegramBot.tgbot.misc.crypt import create_token
from TelegramBot.tgbot.services.MongoDB.users import get_user_by_telegram_id, update_auth_token

login_url = f'{website}/login'


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
    # todo sessions
    await message.answer("Сессии")


def register_account(dp: Dispatcher):
    dp.register_message_handler(bot_account_login, text="Войти на сайт 📲", registered=True)
    dp.register_message_handler(bot_account_sessions, text="Сессии 🖥", registered=True)
