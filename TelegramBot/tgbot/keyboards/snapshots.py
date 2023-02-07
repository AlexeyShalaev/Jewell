import json

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def create_backups_keyboard(files: list):
    keyboard = InlineKeyboardMarkup()
    for file in files:
        keyboard.add(InlineKeyboardButton(file, callback_data=f'snapshot_{file}'))
    keyboard.add(InlineKeyboardButton('Отмена', callback_data=f'snapshot_cancel'))
    return keyboard
