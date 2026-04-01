import aiosqlite


async def init_db(db_path: str, pg_url: str = None, use_postgres: bool = False) -> None:
    if use_postgres and pg_url:
        import asyncpg
        # Remove prefix if using asyncpg directly (it doesn't need postgresql+asyncpg://)
        clean_url = pg_url.replace("postgresql+asyncpg://", "postgresql://")
        
        conn = await asyncpg.connect(clean_url)
        try:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    city_name TEXT NOT NULL DEFAULT 'Москва',
                    city_area_id TEXT NOT NULL DEFAULT '1',
                    filters_json TEXT NOT NULL DEFAULT '{}'
                );
                """
            )
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS favorites (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    vacancy_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    salary TEXT NOT NULL,
                    city TEXT NOT NULL,
                    url TEXT NOT NULL,
                    UNIQUE(user_id, vacancy_id)
                );
                """
            )
        finally:
            await conn.close()
    else:
        async with aiosqlite.connect(db_path) as db:
            await db.execute("PRAGMA journal_mode=WAL;")
            await db.execute("PRAGMA synchronous=NORMAL;")
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    city_name TEXT NOT NULL DEFAULT 'Москва',
                    city_area_id TEXT NOT NULL DEFAULT '1',
                    filters_json TEXT NOT NULL DEFAULT '{}'
                );
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    vacancy_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    salary TEXT NOT NULL,
                    city TEXT NOT NULL,
                    url TEXT NOT NULL,
                    UNIQUE(user_id, vacancy_id)
                );
                """
            )
            await db.commit()
