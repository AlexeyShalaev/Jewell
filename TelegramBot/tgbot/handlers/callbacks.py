from aiogram import types, Dispatcher

from TelegramBot.tgbot.keyboards.sessions import create_submit_keyboard
from TelegramBot.tgbot.misc.notifier import notify_admins
from TelegramBot.tgbot.services.MongoDB.flask_sessions import get_flask_sessions_by_user_id, \
    delete_flask_sessions_by_user_id, delete_flask_session
from TelegramBot.tgbot.services.MongoDB.users import get_user_by_telegram_id
from TelegramBot.tgbot.services.api import snapshot_restore


async def main_callback_query(callback_query: types.CallbackQuery):
    data = callback_query.data
    if data.startswith('session'):
        r = get_user_by_telegram_id(callback_query['from']['id'])
        if r.success:
            user = r.data
            sessions = get_flask_sessions_by_user_id(user.id).data
            index = int(data.split('_')[-1])
            if index == -1:
                delete_flask_sessions_by_user_id(user.id)
            else:
                submit_keyboard = create_submit_keyboard(index)
                await callback_query.message.answer(
                    f'Вы хотите завершить сессию:\n {sessions[index].user_agent} \n {sessions[index].ip}',
                    reply_markup=submit_keyboard)
        await callback_query.message.delete()
    elif data.startswith('submit'):
        answer = data.split('_')
        if answer[-1] == 'true':
            r = get_user_by_telegram_id(callback_query['from']['id'])
            if r.success:
                user = r.data
                sessions = get_flask_sessions_by_user_id(user.id).data
                index = int(data.split('_')[1])
                delete_flask_session(sessions[index].id)
                await callback_query.answer('Вы завершили сессию')
        await callback_query.message.delete()
    elif data.startswith('snapshot'):
        if data == 'snapshot_cancel':
            pass
        else:
            filename = data.split('_', 1)[-1]
            status = snapshot_restore(filename)
            if status:
                notify_admins('Резервное копирование',
                              f'/admin/configuration/backup',
                              'mdi mdi-backup-restore',
                              'danger',
                              f'Восстановлены данные из резервной копии {filename} с помощью телеграм бота пользователем: @{callback_query.from_user.username}.')
                await callback_query.message.answer(f'Вы восстановили данные из резервной копии {filename}')
            else:
                await callback_query.answer('Не удалось восстановить данные из резервной копии')
        await callback_query.message.delete()


def register_callbacks(dp: Dispatcher):
    dp.register_callback_query_handler(main_callback_query)
