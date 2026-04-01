"""
Сервис для работы с PostgreSQL
Хранит фильтры пользователей и статистику
"""

import asyncpg
from typing import Optional, Dict, List
from loguru import logger
from datetime import datetime

from config import settings


class DatabaseService:
    """Сервис для работы с PostgreSQL"""
    
    def __init__(self):
        self.pool = None
    
    async def connect(self):
        """Подключение к БД"""
        try:
            self.pool = await asyncpg.create_pool(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                database=settings.DB_NAME,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                min_size=5,
                max_size=20,
            )
            logger.success("✅ Подключение к PostgreSQL успешно")
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к PostgreSQL: {e}")
            raise
    
    async def disconnect(self):
        """Отключение от БД"""
        if self.pool:
            await self.pool.close()
            logger.info("🔌 Отключение от PostgreSQL")
    
    async def init_schema(self):
        """Создание таблиц БД"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username VARCHAR(255),
                    first_name VARCHAR(255),
                    last_name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS user_filters (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                    filter_name VARCHAR(255),  -- название сохранённого фильтра
                    
                    -- Параметры поиска
                    text VARCHAR(500),  -- ключевые слова
                    area_id INTEGER,  -- ID города
                    area_name VARCHAR(255),  -- имя города
                    
                    -- Опыт, занятость, график
                    experience VARCHAR(50),
                    employment VARCHAR(50),
                    schedule VARCHAR(50),
                    
                    -- Зарплата
                    salary_from INTEGER,
                    salary_to INTEGER,
                    
                    -- Специальные флаги
                    only_with_salary BOOLEAN DEFAULT FALSE,
                    only_direct_employer BOOLEAN DEFAULT FALSE,
                    last_24_hours BOOLEAN DEFAULT FALSE,
                    for_disabled BOOLEAN DEFAULT FALSE,
                    accept_kids BOOLEAN DEFAULT FALSE,  -- для подростков до 18 лет
                    
                    -- Системные поля
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    is_default BOOLEAN DEFAULT FALSE
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS search_history (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                    query TEXT,  -- JSON с параметрами поиска
                    results_count INTEGER,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS favorites (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                    vacancy_id VARCHAR(255),
                    vacancy_title VARCHAR(255),
                    vacancy_data TEXT,  -- JSON с данными вакансии
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            logger.success("✅ Схема БД инициализирована")
    
    # ============ ПОЛЬЗОВАТЕЛИ ============
    
    async def add_user(self, user_id: int, username: str = "", first_name: str = "", last_name: str = ""):
        """Добавить пользователя"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO users (user_id, username, first_name, last_name)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (user_id) DO UPDATE SET
                        updated_at = NOW()
                """, user_id, username, first_name, last_name)
                logger.info(f"👤 Добавлен пользователь: {user_id}")
        except Exception as e:
            logger.error(f"❌ Ошибка добавления пользователя: {e}")
    
    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Получить данные пользователя"""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT * FROM users WHERE user_id = $1", user_id
                )
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"❌ Ошибка получения пользователя: {e}")
            return None
    
    # ============ ФИЛЬТРЫ ============
    
    async def save_filter(self, user_id: int, filter_name: str, filters: Dict):
        """Сохранить фильтры поиска пользователя"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO user_filters 
                    (user_id, filter_name, text, area_id, area_name, experience, 
                     employment, schedule, salary_from, salary_to, 
                     only_with_salary, only_direct_employer, last_24_hours, 
                     for_disabled, accept_kids, is_default)
                    VALUES 
                    ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                """,
                    user_id,
                    filter_name,
                    filters.get("text"),
                    filters.get("area_id"),
                    filters.get("area_name"),
                    filters.get("experience"),
                    filters.get("employment"),
                    filters.get("schedule"),
                    filters.get("salary_from"),
                    filters.get("salary_to"),
                    filters.get("only_with_salary", False),
                    filters.get("only_direct_employer", False),
                    filters.get("last_24_hours", False),
                    filters.get("for_disabled", False),
                    filters.get("accept_kids", False),
                    filters.get("is_default", False)
                )
                logger.info(f"💾 Фильтры пользователя {user_id} сохранены: {filter_name}")
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения фильтров: {e}")
    
    async def get_user_filters(self, user_id: int, filter_name: Optional[str] = None) -> List[Dict]:
        """Получить фильтры пользователя"""
        try:
            async with self.pool.acquire() as conn:
                if filter_name:
                    rows = await conn.fetch(
                        "SELECT * FROM user_filters WHERE user_id = $1 AND filter_name = $2 ORDER BY updated_at DESC",
                        user_id, filter_name
                    )
                else:
                    rows = await conn.fetch(
                        "SELECT * FROM user_filters WHERE user_id = $1 ORDER BY is_default DESC, updated_at DESC",
                        user_id
                    )
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Ошибка получения фильтров: {e}")
            return []
    
    async def delete_filter(self, user_id: int, filter_id: int):
        """Удалить сохранённый фильтр"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    "DELETE FROM user_filters WHERE id = $1 AND user_id = $2",
                    filter_id, user_id
                )
                logger.info(f"🗑️ Фильтр {filter_id} удалён")
        except Exception as e:
            logger.error(f"❌ Ошибка удаления фильтра: {e}")
    
    # ============ ИСТОРИЯ ============
    
    async def add_search_history(self, user_id: int, query: str, results_count: int):
        """Добавить запрос в историю"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    """INSERT INTO search_history (user_id, query, results_count)
                       VALUES ($1, $2, $3)""",
                    user_id, query, results_count
                )
        except Exception as e:
            logger.error(f"❌ Ошибка добавления в историю: {e}")
    
    # ============ ИЗБРАННОЕ ============
    
    async def add_to_favorites(self, user_id: int, vacancy_id: str, title: str, data: str):
        """Добавить вакансию в избранное"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    """INSERT INTO favorites (user_id, vacancy_id, vacancy_title, vacancy_data)
                       VALUES ($1, $2, $3, $4)
                       ON CONFLICT DO NOTHING""",
                    user_id, vacancy_id, title, data
                )
                logger.info(f"⭐ Вакансия добавлена в избранное: {vacancy_id}")
        except Exception as e:
            logger.error(f"❌ Ошибка добавления в избранное: {e}")


# Глобальный экземпляр сервиса
db_service = DatabaseService()


async def init_db():
    """Инициализация БД при запуске"""
    await db_service.connect()
    await db_service.init_schema()
