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

admin = ReplyKeyboardMarkup(resize_keyboard=True). \
    add(KeyboardButton('Назад 🔙')). \
    add(KeyboardButton('Перезапустить сайт 🔃')). \
    add(KeyboardButton('Создать резервную копию 💽️')). \
    add(KeyboardButton('Восстановить из резервной копии 🗃')). \
    add(KeyboardButton('Экcпорт посещаемости в Stars'))

stars_month = ReplyKeyboardMarkup(resize_keyboard=True). \
    add(KeyboardButton('Назад 🔙')). \
    add(KeyboardButton('Stars: сентябрь')). \
    add(KeyboardButton('Stars: октябрь')). \
    add(KeyboardButton('Stars: ноябрь')). \
    add(KeyboardButton('Stars: декабрь')). \
    add(KeyboardButton('Stars: январь')). \
    add(KeyboardButton('Stars: февраль')). \
    add(KeyboardButton('Stars: март')). \
    add(KeyboardButton('Stars: апрель')). \
    add(KeyboardButton('Stars: май')). \
    add(KeyboardButton('Stars: июнь'))

remove = ReplyKeyboardRemove()
