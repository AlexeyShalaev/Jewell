from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

btn_attendance = KeyboardButton('Посещаемость ✅')
btn_account = KeyboardButton('Аккаунт ⚙')
btn_schedule = KeyboardButton('Расписание 📅')
btn_chat = KeyboardButton('Чат 💬')

categories = ReplyKeyboardMarkup(resize_keyboard=True). \
    add(btn_attendance). \
    add(btn_account). \
    add(btn_schedule). \
    add(btn_chat)

remove = ReplyKeyboardRemove()
