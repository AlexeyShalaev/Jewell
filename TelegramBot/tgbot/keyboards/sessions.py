import json

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def create_submit_keyboard(index: int):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Да', callback_data=f'submit_{index}_true'))
    keyboard.add(InlineKeyboardButton('Нет', callback_data=f'submit_{index}_false'))
    return keyboard


def create_keyboard(sessions: list):
    keyboard = InlineKeyboardMarkup()
    for index, session in enumerate(sessions):
        keyboard.add(InlineKeyboardButton(json.dumps(session.ip), callback_data=f'session_{index}'))
    keyboard.add(InlineKeyboardButton('Завершить все сессии', callback_data=f'session_{-1}'))
    return keyboard
