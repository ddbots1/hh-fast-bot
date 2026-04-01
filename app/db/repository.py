import orjson
import time
from typing import Any

import aiosqlite
import asyncpg
from loguru import logger

from app.models.schemas import SearchFilters


class UserRepository:
    def __init__(self, db_path: str, pg_url: str = None, use_postgres: bool = False) -> None:
        self.db_path = db_path
        self.pg_url = pg_url.replace("postgresql+asyncpg://", "postgresql://") if pg_url else None
        self.use_postgres = use_postgres
        self._sqlite_db: aiosqlite.Connection | None = None
        self._pg_pool: asyncpg.Pool | None = None

    async def _get_db(self) -> aiosqlite.Connection:
        if self._sqlite_db is None:
            self._sqlite_db = await aiosqlite.connect(self.db_path)
            await self._sqlite_db.execute("PRAGMA journal_mode=WAL")
            await self._sqlite_db.execute("PRAGMA synchronous=NORMAL")
        return self._sqlite_db

    async def _get_pg_pool(self) -> asyncpg.Pool:
        if self._pg_pool is None:
            self._pg_pool = await asyncpg.create_pool(self.pg_url)
        return self._pg_pool

    async def close(self) -> None:
        if self._sqlite_db:
            await self._sqlite_db.close()
            self._sqlite_db = None
        if self._pg_pool:
            await self._pg_pool.close()
            self._pg_pool = None

    async def ensure_user(self, user_id: int) -> None:
        if self.use_postgres:
            pool = await self._get_pg_pool()
            await pool.execute(
                "INSERT INTO users (user_id) VALUES ($1) ON CONFLICT (user_id) DO NOTHING",
                user_id,
            )
        else:
            db = await self._get_db()
            await db.execute(
                "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
                (user_id,),
            )
            await db.commit()

    async def is_user_exists(self, user_id: int) -> bool:
        if self.use_postgres:
            pool = await self._get_pg_pool()
            row = await pool.fetchrow("SELECT 1 FROM users WHERE user_id = $1", user_id)
            return row is not None
        else:
            db = await self._get_db()
            async with db.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,)) as cursor:
                return await cursor.fetchone() is not None

    async def get_user_count(self) -> int:
        if self.use_postgres:
            pool = await self._get_pg_pool()
            return await pool.fetchval("SELECT COUNT(*) FROM users")
        else:
            db = await self._get_db()
            async with db.execute("SELECT COUNT(*) FROM users") as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def get_filters(self, user_id: int) -> SearchFilters:
        start = time.perf_counter()
        if self.use_postgres:
            pool = await self._get_pg_pool()
            await pool.execute("INSERT INTO users (user_id) VALUES ($1) ON CONFLICT (user_id) DO NOTHING", user_id)
            row = await pool.fetchrow(
                "SELECT filters_json, city_name, city_area_id FROM users WHERE user_id = $1",
                user_id,
            )
            duration = time.perf_counter() - start
            if duration > 0.1:
                logger.warning(f"🐢 Медленное получение фильтров PG ({duration:.3f}s) для {user_id}")
            
            if not row:
                return SearchFilters()
            filters_data = orjson.loads(row["filters_json"] or "{}")
            filters_data["city_name"] = row["city_name"]
            filters_data["city_area_id"] = row["city_area_id"]
            return SearchFilters.from_dict(filters_data)
        else:
            db = await self._get_db()
            await db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
            async with db.execute(
                "SELECT filters_json, city_name, city_area_id FROM users WHERE user_id = ?",
                (user_id,),
            ) as cursor:
                row = await cursor.fetchone()
                duration = time.perf_counter() - start
                if duration > 0.1:
                    logger.warning(f"🐢 Медленное получение фильтров SQLite ({duration:.3f}s) для {user_id}")
                
                if not row:
                    return SearchFilters()
                filters_data = orjson.loads(row[0] or "{}")
                filters_data["city_name"] = row[1]
                filters_data["city_area_id"] = row[2]
                return SearchFilters.from_dict(filters_data)

    async def save_filters(self, user_id: int, filters: SearchFilters) -> None:
        data = filters.to_dict()
        city_name = data.pop("city_name")
        city_area_id = data.pop("city_area_id")
        filters_json = orjson.dumps(data).decode()
        
        if self.use_postgres:
            pool = await self._get_pg_pool()
            await pool.execute(
                """
                UPDATE users
                SET city_name = $1, city_area_id = $2, filters_json = $3
                WHERE user_id = $4
                """,
                city_name, city_area_id, filters_json, user_id,
            )
        else:
            db = await self._get_db()
            await db.execute(
                """
                UPDATE users
                SET city_name = ?, city_area_id = ?, filters_json = ?
                WHERE user_id = ?
                """,
                (city_name, city_area_id, filters_json, user_id),
            )
            await db.commit()

    async def add_favorite(self, user_id: int, item: dict[str, Any]) -> bool:
        if self.use_postgres:
            pool = await self._get_pg_pool()
            try:
                await pool.execute(
                    """
                    INSERT INTO favorites (user_id, vacancy_id, title, salary, city, url)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                    user_id, item["vacancy_id"], item["title"], item["salary"], item["city"], item["url"],
                )
                return True
            except asyncpg.UniqueViolationError:
                return False
        else:
            db = await self._get_db()
            try:
                await db.execute(
                    """
                    INSERT INTO favorites (user_id, vacancy_id, title, salary, city, url)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        item["vacancy_id"],
                        item["title"],
                        item["salary"],
                        item["city"],
                        item["url"],
                    ),
                )
                await db.commit()
                return True
            except aiosqlite.IntegrityError:
                return False

    async def list_favorites(self, user_id: int) -> list[dict[str, str]]:
        if self.use_postgres:
            pool = await self._get_pg_pool()
            rows = await pool.fetch(
                """
                SELECT vacancy_id, title, salary, city, url
                FROM favorites
                WHERE user_id = $1
                ORDER BY id DESC
                LIMIT 30
                """,
                user_id,
            )
            return [dict(row) for row in rows]
        else:
            db = await self._get_db()
            async with db.execute(
                """
                SELECT vacancy_id, title, salary, city, url
                FROM favorites
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT 30
                """,
                (user_id,),
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        "vacancy_id": row[0],
                        "title": row[1],
                        "salary": row[2],
                        "city": row[3],
                        "url": row[4],
                    }
                    for row in rows
                ]
