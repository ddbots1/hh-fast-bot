import orjson
import time
from typing import Any

from redis.asyncio import Redis


class CacheService:
    def __init__(self, redis_url: str, use_redis: bool = True) -> None:
        self.use_redis = use_redis
        self.redis = Redis.from_url(redis_url, decode_responses=True) if use_redis else None
        self._memory: dict[str, tuple[float, str]] = {}

    async def get(self, key: str) -> Any | None:
        if self.use_redis and self.redis:
            raw = await self.redis.get(key)
            return orjson.loads(raw) if raw else None
        row = self._memory.get(key)
        if not row:
            return None
        expires_at, payload = row
        if time.time() > expires_at:
            self._memory.pop(key, None)
            return None
        return orjson.loads(payload)

    async def set(self, key: str, value: Any, ttl: int = 60) -> None:
        payload = orjson.dumps(value).decode()
        if self.use_redis and self.redis:
            await self.redis.set(key, payload, ex=ttl)
            return
        self._memory[key] = (time.time() + ttl, payload)

    async def close(self) -> None:
        if self.redis:
            await self.redis.aclose()
