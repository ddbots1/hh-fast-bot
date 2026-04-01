"""
Клавиатуры Telegram бота
Inline кнопки для фильтров, пагинации и т.д.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import POPULAR_CITIES, EXPERIENCE_CHOICES, EMPLOYMENT_CHOICES, SCHEDULE_CHOICES


class SearchKeyboards:
    """Клавиатуры для поиска"""
    
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Главное меню"""
        keyboard = InlineKeyboardBuilder()
        
        keyboard.add(
            InlineKeyboardButton(text="🔍 Начать поиск", callback_data="search_start"),
            InlineKeyboardButton(text="⭐ Мои фильтры", callback_data="my_filters"),
        )
        keyboard.add(
            InlineKeyboardButton(text="ℹ️ О боте", callback_data="about"),
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings"),
        )
        
        return keyboard.as_markup()
    
    @staticmethod
    def back_button() -> InlineKeyboardMarkup:
        """Кнопка "Назад""""
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu"))
        return keyboard.as_markup()
    
    @staticmethod
    def cities_menu() -> InlineKeyboardMarkup:
        """Меню выбора города"""
        keyboard = InlineKeyboardBuilder()
        
        # Популярные города
        for key, city in POPULAR_CITIES.items():
            keyboard.add(
                InlineKeyboardButton(
                    text=f"📍 {city['name']}",
                    callback_data=f"city_{city['id']}"
                )
            )
        
        keyboard.add(
            InlineKeyboardButton(text="🔍 Другой город", callback_data="custom_city")
        )
        keyboard.add(
            InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_filters")
        )
        
        return keyboard.as_markup()
    
    @staticmethod
    def experience_menu() -> InlineKeyboardMarkup:
        """Меню выбора опыта работы"""
        keyboard = InlineKeyboardBuilder()
        
        options = [
            ("Без опыта", "exp_noExperience"),
            ("1–3 года", "exp_between1And3"),
            ("3–6 лет", "exp_between3And6"),
            ("6+ лет", "exp_moreThan6"),
            ("Не важно", "exp_skip"),
        ]
        
        for text, cb in options:
            keyboard.add(
                InlineKeyboardButton(text=text, callback_data=cb)
            )
        
        keyboard.add(
            InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_filters")
        )
        
        return keyboard.as_markup()
    
    @staticmethod
    def employment_menu() -> InlineKeyboardMarkup:
        """Меню выбора занятости"""
        keyboard = InlineKeyboardBuilder()
        
        options = [
            ("Полная занятость", "emp_full"),
            ("Частичная занятость", "emp_part"),
            ("Проектная работа", "emp_project"),
            ("Стажировка", "emp_probation"),
            ("Не важно", "emp_skip"),
        ]
        
        for text, cb in options:
            keyboard.add(
                InlineKeyboardButton(text=text, callback_data=cb)
            )
        
        keyboard.add(
            InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_filters")
        )
        
        return keyboard.as_markup()
    
    @staticmethod
    def schedule_menu() -> InlineKeyboardMarkup:
        """Меню выбора графика работы"""
        keyboard = InlineKeyboardBuilder()
        
        options = [
            ("Полный день", "sch_fullDay"),
            ("Сменный график", "sch_shift"),
            ("Гибкий график", "sch_flexible"),
            ("Удалённая работа", "sch_remote"),
            ("Вахтовый метод", "sch_flyInFlyOut"),
            ("Не важно", "sch_skip"),
        ]
        
        for text, cb in options:
            keyboard.add(
                InlineKeyboardButton(text=text, callback_data=cb)
            )
        
        keyboard.add(
            InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_filters")
        )
        
        return keyboard.as_markup()
    
    @staticmethod
    def special_filters_menu() -> InlineKeyboardMarkup:
        """Меню специальных фильтров"""
        keyboard = InlineKeyboardBuilder()
        
        options = [
            ("💰 Только с указанной зарплатой", "filter_with_salary"),
            ("🏢 От прямых работодателей", "filter_direct_employer"),
            ("⏰ За последние 24 часа", "filter_last_24h"),
            ("♿ Для людей с инвалидностью", "filter_disabled"),
            ("👶 Доступны с 14 лет (для подростков)", "filter_kids"),
        ]
        
        for text, cb in options:
            keyboard.add(
                InlineKeyboardButton(text=f"☐ {text}", callback_data=cb)
            )
        
        keyboard.add(
            InlineKeyboardButton(text="✅ Начать поиск", callback_data="search_execute"),
            InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_filters")
        )
        
        return keyboard.as_markup()
    
    @staticmethod
    def pagination(page: int, has_next: bool) -> InlineKeyboardMarkup:
        """Кнопки пагинации"""
        keyboard = InlineKeyboardBuilder()
        
        buttons = []
        
        if page > 0:
            buttons.append(
                InlineKeyboardButton(text="⬅️ Предыдущие 3", callback_data=f"page_{page - 1}")
            )
        
        buttons.append(
            InlineKeyboardButton(text=f"📄 {page + 1}", callback_data="current_page")
        )
        
        if has_next:
            buttons.append(
                InlineKeyboardButton(text="Следующие 3 ➡️", callback_data=f"page_{page + 1}")
            )
        
        for btn in buttons:
            keyboard.add(btn)
        
        # Дополнительные кнопки
        keyboard.add(
            InlineKeyboardButton(text="📝 Новый поиск", callback_data="search_start"),
            InlineKeyboardButton(text="🏠 В меню", callback_data="back_to_menu")
        )
        
        return keyboard.as_markup()
    
    @staticmethod
    def vacancy_actions() -> InlineKeyboardMarkup:
        """Кнопки действий для вакансии"""
        keyboard = InlineKeyboardBuilder()
        
        keyboard.add(
            InlineKeyboardButton(text="⭐ В избранное", callback_data="add_to_favorites"),
            InlineKeyboardButton(text="⏭️ Далее", callback_data="next_vacancy"),
        )
        keyboard.add(
            InlineKeyboardButton(text="🏠 В меню", callback_data="back_to_menu")
        )
        
        return keyboard.as_markup()
    
    @staticmethod
    def confirm_search() -> InlineKeyboardMarkup:
        """Кнопки подтверждения поиска"""
        keyboard = InlineKeyboardBuilder()
        
        keyboard.add(
            InlineKeyboardButton(text="✅ Да, начать поиск", callback_data="search_confirm"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="back_to_filters")
        )
        
        return keyboard.as_markup()
    
    @staticmethod
    def filters_summary() -> InlineKeyboardMarkup:
        """Кнопки для сводки фильтров"""
        keyboard = InlineKeyboardBuilder()
        
        keyboard.add(
            InlineKeyboardButton(text="✏️ Изменить", callback_data="edit_filters"),
            InlineKeyboardButton(text="🔍 Поиск", callback_data="search_confirm"),
        )
        keyboard.add(
            InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")
        )
        
        return keyboard.as_markup()
