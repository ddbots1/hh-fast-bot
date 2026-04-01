"""
Сервис для работы с Redis (кэш вакансий и сессии пользователей)
"""

import json
import redis.asyncio as redis
from typing import Optional, Dict, List
from loguru import logger

from config import settings


class CacheService:
    """Сервис для работы с Redis"""
    
    def __init__(self):
        self.redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
        self.ttl = settings.REDIS_TTL
        self.client = None
    
    async def connect(self):
        """Подключение к Redis"""
        try:
            self.client = await redis.from_url(self.redis_url, decode_responses=True)
            # Проверка подключения
            await self.client.ping()
            logger.success("✅ Подключение к Redis успешно")
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к Redis: {e}")
            raise
    
    async def disconnect(self):
        """Отключение от Redis"""
        if self.client:
            await self.client.close()
            logger.info("🔌 Отключение от Redis")
    
    async def get(self, key: str) -> Optional[str]:
        """Получить значение из кэша"""
        try:
            value = await self.client.get(key)
            if value:
                logger.debug(f"✅ Кэш попадание: {key}")
            return value
        except Exception as e:
            logger.error(f"❌ Ошибка чтения из Redis: {e}")
            return None
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None):
        """Сохранить значение в кэш"""
        try:
            ttl = ttl or self.ttl
            await self.client.setex(key, ttl, value)
            logger.debug(f"📝 Кэш установлен: {key} (TTL: {ttl}s)")
        except Exception as e:
            logger.error(f"❌ Ошибка записи в Redis: {e}")
    
    async def delete(self, key: str):
        """Удалить значение из кэша"""
        try:
            await self.client.delete(key)
            logger.debug(f"🗑️ Кэш удалён: {key}")
        except Exception as e:
            logger.error(f"❌ Ошибка удаления из Redis: {e}")
    
    async def get_json(self, key: str) -> Optional[Dict]:
        """Получить JSON из кэша"""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                logger.warning(f"⚠️ Ошибка декодирования JSON: {key}")
                return None
        return None
    
    async def set_json(self, key: str, value: Dict, ttl: Optional[int] = None):
        """Сохранить JSON в кэш"""
        try:
            json_str = json.dumps(value, ensure_ascii=False)
            await self.set(key, json_str, ttl)
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения JSON: {e}")
    
    async def set_user_filters(self, user_id: int, filters: Dict):
        """Сохранить фильтры пользователя в Redis (для быстрого доступа)"""
        key = f"user_filters:{user_id}"
        await self.set_json(key, filters, ttl=86400)  # 24 часа
        logger.info(f"💾 Фильтры пользователя {user_id} сохранены в Redis")
    
    async def get_user_filters(self, user_id: int) -> Optional[Dict]:
        """Получить фильтры пользователя из Redis"""
        key = f"user_filters:{user_id}"
        return await self.get_json(key)
    
    async def cache_search_results(self, cache_key: str, vacancies: List[Dict]):
        """Кэшировать результаты поиска"""
        await self.set_json(cache_key, vacancies, ttl=3600)  # 1 час
        logger.info(f"💾 Результаты поиска закэшированы: {cache_key}")
    
    async def get_cached_search(self, cache_key: str) -> Optional[List[Dict]]:
        """Получить закэшированные результаты"""
        results = await self.get_json(cache_key)
        if results:
            logger.info(f"✅ Результаты получены из кэша: {cache_key}")
        return results


# Глобальный экземпляр сервиса
cache_service = CacheService()


async def init_redis():
    """Инициализация Redis при запуске"""
    await cache_service.connect()
