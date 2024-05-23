from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def research_or_connect_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Искать заново", callback_data="search_again"))
    keyboard.add(InlineKeyboardButton("Связаться с оператором", callback_data="transfer_to_operator"))
    return keyboard

def operator_control_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Завершить разговор", callback_data="end_conversation"))
    keyboard.add(InlineKeyboardButton("Заблокировать пользователя", callback_data="block_user"))
    keyboard.add(InlineKeyboardButton("Разблокировать пользователя", callback_data="unblock_user"))
    return keyboard