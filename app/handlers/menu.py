from aiogram import F, Router
from aiogram.types import Message

from app.config import settings
from app.db.repository import UserRepository
from app.keyboards.filters import filters_root_kb

router = Router()


@router.message(F.text == "📍 Мой город")
async def my_city(message: Message, user_repo: UserRepository) -> None:
    filters = await user_repo.get_filters(message.from_user.id)
    await message.answer(f"Твой текущий город: *{filters.city_name}*")


@router.message(F.text == "🎛 Фильтры")
async def filters_menu(message: Message) -> None:
    await message.answer("Выбери фильтр:", reply_markup=filters_root_kb())


@router.message(F.text == "💰 Партнерки")
async def partner_info(message: Message) -> None:
    await message.answer("Партнерская вакансия всегда первая в выдаче и подбирается по твоему городу.")
