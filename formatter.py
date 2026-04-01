"""
Сервис для форматирования вакансий в красивый текст
"""

from typing import List
from models import Vacancy


class FormatterService:
    """Форматирование вакансий для Telegram"""
    
    @staticmethod
    def format_vacancy(vacancy: Vacancy, add_button: bool = True) -> str:
        """
        Форматирует одну вакансию в красивый текст
        
        Args:
            vacancy: объект Vacancy
            add_button: добавить кнопку "Подробнее"
        
        Returns:
            Отформатированная строка
        """
        
        # Заголовок с эмодзи
        text = f"🔥 **{vacancy.name}**\n"
        
        # Основная информация
        info_parts = []
        
        if vacancy.area:
            info_parts.append(f"📍 {vacancy.area.name}")
        
        if vacancy.salary:
            salary_str = vacancy.salary.format()
            info_parts.append(f"💰 {salary_str}")
        else:
            info_parts.append("💰 По договорённости")
        
        # Объединяем в одну строку
        if info_parts:
            text += " • ".join(info_parts) + "\n"
        
        # Условия работы
        conditions = []
        
        if vacancy.employment:
            employment = vacancy.employment.get("name", "")
            if employment:
                conditions.append(employment)
        
        if vacancy.schedule:
            schedule = vacancy.schedule.get("name", "")
            if schedule:
                conditions.append(schedule)
        
        if conditions:
            text += "🕒 " + " • ".join(conditions) + "\n"
        
        # Опыт работы
        if vacancy.experience:
            exp = vacancy.experience.get("name", "")
            if exp:
                text += f"👤 {exp}\n"
        
        # Компания (если есть)
        if vacancy.employer_name:
            text += f"🏢 {vacancy.employer_name}\n"
        
        # Описание должности
        if vacancy.snippet_responsibility:
            description = vacancy.snippet_responsibility[:150]
            if len(vacancy.snippet_responsibility) > 150:
                description += "..."
            text += f"\n_{description}_\n"
        
        # Требования
        if vacancy.snippet_requirement:
            requirement = vacancy.snippet_requirement[:100]
            if len(vacancy.snippet_requirement) > 100:
                requirement += "..."
            text += f"\n**Требования:** {requirement}\n"
        
        # Кнопка
        if add_button:
            text += f"\n[👉 Подробнее на HH →]({vacancy.alternate_url or vacancy.url})"
        
        return text
    
    @staticmethod
    def format_partner_vacancy(partner: dict, add_button: bool = True) -> str:
        """
        Форматирует партнёрскую вакансию
        (выглядит как настоящая, но это реклама)
        
        Args:
            partner: словарь с партнёрской вакансией
            add_button: добавить кнопку
        
        Returns:
            Отформатированная строка
        """
        
        text = f"{partner.get('emoji', '🔥')} **{partner.get('title', '')}**\n"
        
        # Основная информация
        info_parts = []
        
        if partner.get('salary'):
            info_parts.append(f"💰 {partner['salary']}")
        
        info_str = partner.get('schedule', '')
        if info_str:
            info_parts.append(info_str)
        
        if info_parts:
            text += " • ".join(info_parts) + "\n"
        
        # Описание
        if partner.get('description'):
            desc = partner['description']
            if len(desc) > 150:
                desc = desc[:150] + "..."
            text += f"\n_{desc}_\n"
        
        # Кнопка
        if add_button:
            button_text = partner.get('button_text', 'Подробнее →')
            url = partner.get('url', 'https://example.com')
            text += f"\n[👉 {button_text}]({url})"
        
        return text
    
    @staticmethod
    def format_vacancies_pack(
        vacancies: List[Vacancy],
        partner_vacancy: dict = None,
        page: int = 0
    ) -> str:
        """
        Форматирует пакет из 3 вакансий (1 партнёрка + 2 реальные)
        
        Args:
            vacancies: список вакансий
            partner_vacancy: словарь партнёрской вакансии
            page: номер страницы (для статистики)
        
        Returns:
            Отформатированная строка со всеми вакансиями
        """
        
        text = ""
        
        # Партнёрская вакансия на первой позиции
        if partner_vacancy:
            text += FormatterService.format_partner_vacancy(partner_vacancy)
            text += "\n\n" + "─" * 40 + "\n\n"
        
        # Остальные вакансии
        for i, vacancy in enumerate(vacancies[:2], 1):
            text += FormatterService.format_vacancy(vacancy)
            if i < len(vacancies[:2]):
                text += "\n\n" + "─" * 40 + "\n\n"
        
        # Информация о странице
        text += f"\n\n_Страница {page + 1}_"
        
        return text
    
    @staticmethod
    def format_search_start() -> str:
        """Приветствие при начале поиска"""
        return """
🔍 **Начнём поиск!**

Укажите параметры поиска:
1️⃣ Введите должность или ключевые слова
2️⃣ Выберите город
3️⃣ Задайте дополнительные фильтры (зарплата, опыт и т.д.)

Или используйте быстрые фильтры 👇
"""
    
    @staticmethod
    def format_no_results() -> str:
        """Сообщение при отсутствии результатов"""
        return """
😔 **По вашему запросу вакансий не найдено**

Попробуйте:
• Изменить ключевые слова
• Выбрать другой город
• Снять некоторые фильтры

📝 Начните поиск заново в меню
"""
    
    @staticmethod
    def format_error() -> str:
        """Сообщение об ошибке"""
        return """
⚠️ **Ошибка при поиске вакансий**

Сервис временно недоступен. Попробуйте позже.

💬 Если ошибка повторяется, напишите @support
"""
