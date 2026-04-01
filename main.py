import asyncio

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from loguru import logger

from app.config import settings
from app.db.database import init_db
from app.db.repository import UserRepository
from app.handlers import register_routers
from app.logging_config import setup_logging
from app.middlewares.antiflood import AntiFloodMiddleware
from app.services.cache import CacheService
from app.services.hh_api import HHClient
from app.services.partner import PartnerService
from app.services.search import SearchService
from app.services.stats import DailyStatsService


async def main() -> None:
    setup_logging()
    await init_db(
        db_path=settings.db_path,
        pg_url=settings.pg_url,
        use_postgres=settings.use_postgres,
    )

    # session = None
    # if settings.telegram_proxy:
    #     from aiogram.client.session.aiohttp import AiohttpSession

    #     session = AiohttpSession(proxy=settings.telegram_proxy)

    try:
        # aiogram >= 3.7
        from aiogram.client.default import DefaultBotProperties

        bot = Bot(
            token=settings.bot_token,
            session=None,  # Принудительно отключаем прокси
            default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
        )
    except ModuleNotFoundError:
        # aiogram 3.0-3.6 fallback
        bot = Bot(token=settings.bot_token, parse_mode=ParseMode.MARKDOWN, session=None)
    if settings.use_redis:
        from aiogram.fsm.storage.redis import RedisStorage
        from redis.asyncio import Redis as AsyncRedis

        redis_fsm = AsyncRedis.from_url(settings.redis_url)
        storage = RedisStorage(redis=redis_fsm)
        logger.info("Используется Redis для FSM")
    else:
        from aiogram.fsm.storage.memory import MemoryStorage

        storage = MemoryStorage()
        logger.info("Используется MemoryStorage для FSM")

    dp = Dispatcher(storage=storage)

    user_repo = UserRepository(
        db_path=settings.db_path,
        pg_url=settings.pg_url,
        use_postgres=settings.use_postgres,
    )
    cache = CacheService(redis_url=settings.redis_url, use_redis=settings.use_redis)
    hh_client = HHClient(base_url=settings.hh_api_base_url)
    partner_service = PartnerService()
    stats_service = DailyStatsService()
    search_service = SearchService(
        hh_client=hh_client,
        cache=cache,
        partner_service=partner_service,
    )

    dp.update.middleware(AntiFloodMiddleware(settings.anti_flood_seconds, cache))
    dp["search_service"] = search_service
    dp["stats_service"] = stats_service
    dp["user_repo"] = user_repo

    register_routers(dp)

    found_today = stats_service.get_today_found_counter()
    logger.info("Сегодня уже нашли работу {} человек 🔥", found_today)

    try:
        await dp.start_polling(bot)
    finally:
        await user_repo.close()
        await hh_client.close()
        await cache.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
