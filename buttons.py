from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
button4 = KeyboardButton('Поделиться Геолокацией🌍', request_location=True)
buttonGeo = ReplyKeyboardMarkup(resize_keyboard=True).add(button4)