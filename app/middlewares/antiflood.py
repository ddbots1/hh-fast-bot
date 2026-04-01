import time
from collections import defaultdict
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject


from app.services.cache import CacheService


class AntiFloodMiddleware(BaseMiddleware):
    def __init__(self, seconds: float, cache: CacheService) -> None:
        self.seconds = seconds
        self.cache = cache

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)

        # Не блокируем callback-клики, иначе ломается многошаговый flow фильтров.
        if isinstance(event, CallbackQuery):
            return await handler(event, data)

        # Ограничиваем только частые текстовые сообщения.
        if not isinstance(event, Message):
            return await handler(event, data)

        cache_key = f"antiflood_{user.id}"
        last_hit = await self.cache.get(cache_key)
        now = time.time()

        if last_hit and now - last_hit < self.seconds:
            return None

        await self.cache.set(cache_key, now, ttl=int(self.seconds) + 1)
        return await handler(event, data)
