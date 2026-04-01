from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.utils.constants import AGE_LABELS_MAP, EMPLOYMENT_MAP, EXPERIENCE_MAP, SCHEDULE_MAP


def filters_root_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📍 Город", callback_data="flt:city")],
            [InlineKeyboardButton(text="👤 Возраст", callback_data="flt:age")],
            [InlineKeyboardButton(text="🕒 Занятость", callback_data="flt:employment")],
            [InlineKeyboardButton(text="📆 График", callback_data="flt:schedule")],
            [InlineKeyboardButton(text="💼 Опыт", callback_data="flt:experience")],
            [InlineKeyboardButton(text="💰 Зарплата", callback_data="flt:salary")],
            [InlineKeyboardButton(text="🔎 Ключевые слова", callback_data="flt:text_hint")],
            [InlineKeyboardButton(text="✅ Искать сейчас", callback_data="flt:run")],
        ]
    )


def age_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=title, callback_data=f"set:age:{code}")]
            for _, (title, code) in AGE_LABELS_MAP.items()
        ]
        + [
            [InlineKeyboardButton(text="Сбросить", callback_data="set:age:")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="flt:back_filters")],
        ]
    )


def employment_kb() -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=v[0], callback_data=f"set:employment:{v[1]}")] for v in EMPLOYMENT_MAP.values()]
    rows.append([InlineKeyboardButton(text="Сбросить", callback_data="set:employment:")])
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="flt:age")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def schedule_kb() -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=v[0], callback_data=f"set:schedule:{v[1]}")] for v in SCHEDULE_MAP.values()]
    rows.append([InlineKeyboardButton(text="Сбросить", callback_data="set:schedule:")])
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="flt:employment")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def experience_kb() -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=v[0], callback_data=f"set:experience:{v[1]}")] for v in EXPERIENCE_MAP.values()]
    rows.append([InlineKeyboardButton(text="Сбросить", callback_data="set:experience:")])
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="flt:schedule")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def keyword_step_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⏭ Пропустить ключевые слова", callback_data="flt:skip_text")],
            [InlineKeyboardButton(text="🔎 Показать вакансии", callback_data="flt:run")],
            [InlineKeyboardButton(text="🎛 Вернуться к фильтрам", callback_data="flt:back_filters")],
        ]
    )


def city_after_pick_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⚡ Быстрый режим: Показать вакансии", callback_data="flt:quick_run")],
            [InlineKeyboardButton(text="🎛 Настроить фильтры", callback_data="flt:age")],
        ]
    )


def salary_step_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="flt:experience")],
            [InlineKeyboardButton(text="⏭ Пропустить зарплату", callback_data="flt:skip_salary")],
        ]
    )
