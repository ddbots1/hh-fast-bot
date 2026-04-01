from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def vacancy_actions_kb(url: str, vacancy_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🚀 Откликнуться", url=url),
                InlineKeyboardButton(text="⭐ В избранное", callback_data=f"fav:add:{vacancy_id}"),
            ],
            [
                InlineKeyboardButton(text="📤 Поделиться", switch_inline_query=f"Посмотри эту вакансию: {url}"),
            ],
        ]
    )


def partner_actions_kb(url: str, button_text: str = "Перейти в партнерку") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"⚡ {button_text}", url=url)],
        ]
    )


def pagination_kb(page: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="← Предыдущие", callback_data=f"page:{max(0, page - 1)}"),
                InlineKeyboardButton(text="Следующие 3 →", callback_data=f"page:{page + 1}"),
            ],
            [
                InlineKeyboardButton(text="🔍 Новый поиск", callback_data="nav:new_search"),
                InlineKeyboardButton(text="🎛 Фильтры", callback_data="nav:filters"),
            ],
        ]
    )
