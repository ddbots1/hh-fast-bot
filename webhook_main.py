import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from loguru import logger

from app.config import settings
from app.db.database import init_db
from app.handlers import register_routers
from app.logging_config import setup_logging
from app.middlewares.antiflood import AntiFloodMiddleware
from app.services.cache import CacheService
from app.services.hh_api import HHClient
from app.services.partner import PartnerService
from app.services.search import SearchService
from app.services.stats import DailyStatsService

# Настройки для вебхуков
WEBHOOK_PATH = f"{settings.webhook_path}{settings.bot_token}"
WEBHOOK_URL = f"{settings.webhook_host}{WEBHOOK_PATH}"


async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(WEBHOOK_URL)
    logger.info("Вебхук установлен: {}", WEBHOOK_URL)


async def main() -> None:
    setup_logging()
    await init_db(settings.db_path)

    if settings.use_redis:
        from aiogram.fsm.storage.redis import RedisStorage
        from redis.asyncio import Redis as AsyncRedis
        redis_fsm = AsyncRedis.from_url(settings.redis_url)
        storage = RedisStorage(redis=redis_fsm)
    else:
        from aiogram.fsm.storage.memory import MemoryStorage
        storage = MemoryStorage()

    dp = Dispatcher(storage=storage)
    bot = Bot(token=settings.bot_token, parse_mode=ParseMode.MARKDOWN)

    cache = CacheService(redis_url=settings.redis_url, use_redis=settings.use_redis)
    hh_client = HHClient(base_url=settings.hh_api_base_url)
    partner_service = PartnerService()
    stats_service = DailyStatsService()
    search_service = SearchService(hh_client=hh_client, cache=cache, partner_service=partner_service)

    dp.update.middleware(AntiFloodMiddleware(settings.anti_flood_seconds, cache))
    dp["search_service"] = search_service
    dp["stats_service"] = stats_service

    register_routers(dp)
    dp.startup.register(on_startup)

    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, settings.web_server_host, settings.web_server_port)
    await site.start()
    
    logger.info("Сервер вебхуков запущен на {}:{}", settings.web_server_host, settings.web_server_port)
    
    try:
        await asyncio.Event().wait()
    finally:
        await hh_client.close()
        await cache.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
