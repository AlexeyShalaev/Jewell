from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

btn_login = KeyboardButton('Войти на сайт 📲')
btn_sessions = KeyboardButton('Сессии 🖥')
btn_back = KeyboardButton('Назад 🔙')

registered = ReplyKeyboardMarkup(resize_keyboard=True). \
    add(btn_login). \
    add(btn_sessions).\
    add(btn_back)

remove = ReplyKeyboardRemove()
