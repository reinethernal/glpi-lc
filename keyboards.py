from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def research_or_connect_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Попробовать ещё раз", callback_data="search_again"))
    keyboard.add(InlineKeyboardButton("Связаться с оператором", callback_data="transfer_to_operator"))
    return keyboard

def operator_keyboard():
    return InlineKeyboardMarkup().add(InlineKeyboardButton("Ответить", callback_data="answer"))

