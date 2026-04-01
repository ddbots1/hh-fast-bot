"""
Модели данных для вакансий
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Salary:
    """Информация о зарплате"""
    from_amount: Optional[int] = None
    to_amount: Optional[int] = None
    currency: str = "RUR"
    
    def format(self) -> str:
        """Красиво форматирует зарплату"""
        if not self.from_amount and not self.to_amount:
            return "По договорённости"
        
        if self.from_amount and self.to_amount:
            return f"{self.from_amount:,} — {self.to_amount:,} ₽".replace(",", " ")
        elif self.from_amount:
            return f"От {self.from_amount:,} ₽".replace(",", " ")
        else:
            return f"До {self.to_amount:,} ₽".replace(",", " ")


@dataclass
class Area:
    """Информация о городе"""
    id: int
    name: str
    
    def __str__(self):
        return self.name


@dataclass
class Vacancy:
    """Вакансия с HH.ru"""
    
    # Основная информация
    id: str
    name: str  # Название должности
    url: str  # Ссылка на вакансию
    alternate_url: str = ""
    
    # Зарплата
    salary: Optional[Salary] = None
    
    # Место работы
    area: Optional[Area] = None
    employer_name: str = ""
    employer_logo_url: str = ""
    
    # Описание
    snippet_requirement: str = ""  # Требуемый опыт
    snippet_responsibility: str = ""  # Основные обязанности
    
    # Условия работы
    employment: dict = None  # {"id": "full", "name": "Полная занятость"}
    schedule: dict = None  # {"id": "fullDay", "name": "Полный день"}
    experience: dict = None  # {"id": "between1And3", "name": "1–3 года"}
    
    # Дополнительно
    published_at: str = ""
    created_at: str = ""
    response_letter_required: bool = False
    
    def format_short(self) -> str:
        """Короткий формат вакансии для вывода"""
        salary_str = self.salary.format() if self.salary else "По договорённости"
        
        # Собираем информацию
        info_parts = []
        
        if self.area:
            info_parts.append(f"📍 {self.area.name}")
        
        info_parts.append(f"💰 {salary_str}")
        
        if self.employment:
            info_parts.append(f"🕒 {self.employment.get('name', '')}")
        
        if self.schedule:
            info_parts.append(f"🗓️ {self.schedule.get('name', '')}")
        
        experience_str = ""
        if self.experience:
            exp_name = self.experience.get('name', '')
            if exp_name:
                experience_str = f"👤 {exp_name}"
        
        info = " • ".join(info_parts)
        
        result = f"🔥 **{self.name}**\n"
        result += f"{info}\n"
        if experience_str:
            result += f"{experience_str}\n"
        result += f"\n{self.snippet_responsibility[:100]}...\n\n"
        result += f"👉 [Подробнее→]({self.alternate_url or self.url})"
        
        return result
    
    def to_dict(self) -> dict:
        """Преобразует в словарь для кэша"""
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "salary": {
                "from": self.salary.from_amount if self.salary else None,
                "to": self.salary.to_amount if self.salary else None,
            },
            "area": self.area.name if self.area else "",
            "employer": self.employer_name,
            "employment": self.employment.get('name', '') if self.employment else "",
            "schedule": self.schedule.get('name', '') if self.schedule else "",
            "experience": self.experience.get('name', '') if self.experience else "",
            "description": self.snippet_responsibility,
        }
