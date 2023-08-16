from aiogram import types, Dispatcher

from TelegramBot.tgbot.keyboards import menu
from TelegramBot.tgbot.services.MongoDB.users import get_user_by_access_token, update_telegram_data, \
    get_user_by_telegram_id


async def bot_messages(message: types.Message):
    if len(message.text) == 32:
        r = get_user_by_telegram_id(message.from_user.id)
        if r.success:
            await message.answer("Данный телеграм аккаунт уже привязан.", reply_markup=menu.categories)
        else:
            r = get_user_by_access_token(message.text)
            if not r.success:
                await message.answer('Неизвестный ключ', reply_markup=menu.categories)
            else:
                update_telegram_data(r.data.id, message.from_user.id, message.from_user.username)
                await message.answer(
                    'Ваш телеграм успешно привязан к аккаунту.',
                    reply_markup=menu.categories)


def register_messages(dp: Dispatcher):
    dp.register_message_handler(bot_messages, content_types=['text'])
