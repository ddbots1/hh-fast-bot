from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 Новый поиск"), KeyboardButton(text="📍 Мой город")],
            [KeyboardButton(text="🎛 Фильтры"), KeyboardButton(text="⭐ Избранное")],
            [KeyboardButton(text="💰 Партнерки")],
        ],
        resize_keyboard=True,
    )
