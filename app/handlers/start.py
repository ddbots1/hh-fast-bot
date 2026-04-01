from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.config import settings
from app.db.repository import UserRepository
from app.keyboards.main_menu import main_menu_kb
from app.services.stats import DailyStatsService

router = Router()


@router.message(CommandStart())
async def start_cmd(
    message: Message, stats_service: DailyStatsService, user_repo: UserRepository
) -> None:
    user_id = message.from_user.id

    # Проверка на лимит пользователей
    if not await user_repo.is_user_exists(user_id):
        count = await user_repo.get_user_count()
        if count >= settings.max_users:
            await message.answer(
                "Извините, в данный момент бот достиг максимального количества пользователей.\n"
                "Попробуйте зайти позже."
            )
            return

    await user_repo.ensure_user(user_id)
    found_today = stats_service.get_today_found_counter()

    if settings.start_video_url:
        await message.answer_video(
            settings.start_video_url,
            caption="🎬 Быстрый старт: выберите фильтры и нажмите «Новый поиск».",
        )

    await message.answer(
        "Привет! Я *HH Fast* — быстрый HR-бот для поиска вакансий.\n\n"
        f"Сегодня уже нашли работу *{found_today}* человек 🔥\n"
        "Нажми «🔍 Новый поиск», и я покажу 7 свежих вакансий + партнерку сверху.",
        reply_markup=main_menu_kb(),
    )
