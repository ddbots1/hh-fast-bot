"""
Конфигурация HH Fast Bot
Читает переменные из .env файла
"""

from pydantic_settings import BaseSettings
from pydantic import Field
import os


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Telegram
    BOT_TOKEN: str = Field(..., alias="8229276656:AAFeBfH9eVKNKge1JG-SvNegmp40IuCq1pA")
    
    # PostgreSQL
    DB_HOST: str = Field(default="localhost")
    DB_PORT: int = Field(default=5432)
    DB_NAME: str = Field(default="hh_fast_bot")
    DB_USER: str = Field(default="postgres")
    DB_PASSWORD: str = Field(...)
    
    # Redis
    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)
    REDIS_DB: int = Field(default=0)
    REDIS_TTL: int = Field(default=3600)  # Время кэша в секундах (1 час)
    
    # HH.ru API
    HH_API_BASE: str = Field(default="https://api.hh.ru")
    HH_VACANCIES_PER_PAGE: int = Field(default=20)
    HH_REQUEST_TIMEOUT: int = Field(default=10)
    
    # Логирование
    LOG_LEVEL: str = Field(default="INFO")
    
    # Бизнес-логика
    VACANCIES_PER_MESSAGE: int = Field(default=3)  # Вакансий на одном сообщении
    PARTNER_POSITION: int = Field(default=0)  # На какой позиции партнёрка (0 = первая)
    ANTI_FLOOD_DELAY: float = Field(default=0.5)  # Задержка между сообщениями
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Инициализация настроек
settings = Settings()


# Словари для фильтров HH.ru
EXPERIENCE_CHOICES = {
    "noExperience": "Без опыта",
    "between1And3": "1–3 года",
    "between3And6": "3–6 лет",
    "moreThan6": "6+ лет",
}

EMPLOYMENT_CHOICES = {
    "full": "Полная занятость",
    "part": "Частичная занятость",
    "project": "Проектная работа",
    "probation": "Стажировка",
}

SCHEDULE_CHOICES = {
    "fullDay": "Полный день",
    "shift": "Сменный график",
    "flexible": "Гибкий график",
    "remote": "Удалённая работа",
    "flyInFlyOut": "Вахтовый метод",
}

# Популярные города (для быстрого выбора)
POPULAR_CITIES = {
    "moscow": {"id": 1, "name": "Москва"},
    "spb": {"id": 2, "name": "Санкт-Петербург"},
    "novosibirsk": {"id": 3, "name": "Новосибирск"},
    "yekaterinburg": {"id": 4, "name": "Екатеринбург"},
    "kazan": {"id": 5, "name": "Казань"},
    "perm": {"id": 6, "name": "Пермь"},
    "voronezh": {"id": 8, "name": "Воронеж"},
    "tyumen": {"id": 33, "name": "Тюмень"},
    "krasnodar": {"id": 53, "name": "Краснодар"},
    "omsk": {"id": 104, "name": "Омск"},
}

# Антифлуд параметры
FLOOD_THRESHOLD = 5  # Количество команд
FLOOD_TIMEOUT = 60  # За сколько секунд
