import json

from aiogram import types, Dispatcher

from TelegramBot.tgbot.keyboards import menu
from TelegramBot.tgbot.services.MongoDB.users import get_user_by_access_token, update_telegram_data, \
    get_user_by_telegram_id
from TelegramBot.tgbot.services.api import animation_add


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


async def bot_animation(message: types.Animation):
    user = get_user_by_telegram_id(message.from_user.id).data
    await message.answer(
        'Идет обработка анимации...',
        reply_markup=menu.categories)
    try:
        file_id = message.sticker.file_id
        file_info = await message.bot.get_file(file_id)
        file = await message.bot.download_file(file_info.file_path)
        file_extension = file_info.file_path.split('.')[-1]
        if animation_add(str(user.id), file, file_extension):
            await message.answer(
                'Анимация на зеркале обновлена.',
                reply_markup=menu.categories)
        else:
            await message.answer(
                'Не удалось обновить анимацию на зеркале.',
                reply_markup=menu.categories)
    except Exception as ex:
        print(ex)


def register_messages(dp: Dispatcher):
    dp.register_message_handler(bot_messages, content_types=['text'])
    dp.register_message_handler(bot_animation, content_types=['sticker', 'animation'], registered=True)
