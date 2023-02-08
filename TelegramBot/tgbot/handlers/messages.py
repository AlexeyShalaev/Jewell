from aiogram import types, Dispatcher

from TelegramBot.tgbot.services.MongoDB.users import get_user_by_access_token, update_telegram_data, \
    get_user_by_telegram_id


async def bot_messages(message: types.Message):
    if len(message.text) == 32:
        r = get_user_by_telegram_id(message.from_user.id)
        if r.success:
            await message.answer("Данный телеграм аккаунт уже привязан.")
        else:
            r = get_user_by_access_token(message.text)
            if not r.success:
                await message.answer('Неизвестный ключ')
            else:
                update_telegram_data(r.data.id, message.from_user.id, message.from_user.username)
                await message.answer('Ваш телеграм успешно привязан к аккаунту.\nСовет: включите в настройках сайта авторизацию через телеграм.')


def register_messages(dp: Dispatcher):
    dp.register_message_handler(bot_messages, content_types=['text'])
