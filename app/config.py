from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv

# Ищем .env в текущей папке или на уровень выше (корень проекта)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
load_dotenv() # Повторный вызов для системных переменных



@dataclass(slots=True)
class Settings:
    bot_token: str = os.getenv("BOT_TOKEN", "8229276656:AAFeBfH9eVKNKge1JG-SvNegmp40IuCq1pA")
    telegram_proxy: str = os.getenv("TELEGRAM_PROXY", "")
    hh_api_base_url: str = os.getenv("HH_API_BASE_URL", "https://api.hh.ru")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    use_redis: bool = os.getenv("USE_REDIS", "true").lower() == "true"
    db_path: str = os.getenv("DB_PATH", "bot.db")
    
    # PostgreSQL settings
    pg_url: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/db")
    use_postgres: bool = os.getenv("USE_POSTGRES", "false").lower() == "true"

    start_video_url: str = os.getenv("START_VIDEO_URL", "")
    anti_flood_seconds: float = float(os.getenv("ANTI_FLOOD_SECONDS", "1.0"))
    max_users: int = int(os.getenv("MAX_USERS", "5000"))

    # Webhook settings
    webhook_host: str = os.getenv("WEBHOOK_HOST", "https://your-domain.com")
    webhook_path: str = os.getenv("WEBHOOK_PATH", f"/webhook/")
    web_server_host: str = os.getenv("WEB_SERVER_HOST", "0.0.0.0")
    web_server_port: int = int(os.getenv("WEB_SERVER_PORT", "8080"))


settings = Settings()

if not settings.bot_token:
    raise RuntimeError("BOT_TOKEN is empty. Set BOT_TOKEN in .env file.")
