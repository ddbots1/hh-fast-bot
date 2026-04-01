import asyncio

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from loguru import logger

from app.config import settings
from app.db.repository import UserRepository
from app.handlers.states import FilterInputState
from app.keyboards.filters import filters_root_kb
from app.keyboards.results import pagination_kb, partner_actions_kb, vacancy_actions_kb
from app.services.search import SearchService
from app.utils.formatters import format_partner_text, format_vacancy_text

router = Router()


async def _send_search_results(
    message: Message, search_service: SearchService, user_id: int, user_repo: UserRepository
) -> None:
    filters = await user_repo.get_filters(user_id)
    params = filters.to_hh_params()

    partner, vacancies = await asyncio.gather(
        search_service.get_partner(filters.city_name),
        search_service.get_vacancies(params),
    )

    if filters.page == 0:
        await message.answer(
            format_partner_text(partner),
            reply_markup=partner_actions_kb(partner["url"], partner.get("button_text", "Перейти в партнерку")),
        )
    for item in vacancies[:3]:
        await message.answer(format_vacancy_text(item), reply_markup=vacancy_actions_kb(item["url"], item["vacancy_id"]))
    await message.answer(f"Страница {filters.page + 1}", reply_markup=pagination_kb(filters.page))


@router.message(F.text == "🔍 Новый поиск")
async def new_search(message: Message, state: FSMContext) -> None:
    await state.set_state(FilterInputState.waiting_city)
    await message.answer("Начнем с города. Введи город или населенный пункт РФ.")
    await message.answer("После выбора города настроишь фильтры:", reply_markup=filters_root_kb())


@router.callback_query(F.data == "flt:run")
async def run_search_from_filters(
    call: CallbackQuery, search_service: SearchService, user_repo: UserRepository
) -> None:
    try:
        filters = await user_repo.get_filters(call.from_user.id)
        filters.page = 0
        await user_repo.save_filters(call.from_user.id, filters)
        await _send_search_results(call.message, search_service, call.from_user.id, user_repo)
        await call.answer("Готово")
    except Exception as exc:
        logger.exception(exc)
        await call.answer("Ошибка поиска", show_alert=True)


@router.callback_query(F.data == "flt:quick_run")
async def quick_run(call: CallbackQuery, search_service: SearchService, user_repo: UserRepository) -> None:
    try:
        filters = await user_repo.get_filters(call.from_user.id)
        # Быстрый режим: только город + выдача
        filters.page = 0
        filters.age_from = ""
        filters.employment = ""
        filters.schedule = ""
        filters.experience = ""
        filters.salary_from = ""
        filters.salary_to = ""
        filters.text = ""
        await user_repo.save_filters(call.from_user.id, filters)
        await _send_search_results(call.message, search_service, call.from_user.id, user_repo)
        await call.answer("Быстрый режим запущен")
    except Exception as exc:
        logger.exception(exc)
        await call.answer("Ошибка поиска", show_alert=True)


@router.callback_query(F.data.startswith("page:"))
async def pagination(call: CallbackQuery, search_service: SearchService, user_repo: UserRepository) -> None:
    page = int(call.data.split(":")[1])
    filters = await user_repo.get_filters(call.from_user.id)
    filters.page = max(0, page)
    await user_repo.save_filters(call.from_user.id, filters)
    
    # Редактируем текущее сообщение для создания эффекта Skeleton Loading
    try:
        await call.message.edit_text("🔍 _Ищу лучшие предложения..._")
    except Exception:
        pass
        
    await _send_search_results(call.message, search_service, call.from_user.id, user_repo)
    await call.answer()


@router.callback_query(F.data == "nav:new_search")
async def nav_new_search(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(FilterInputState.waiting_city)
    await call.message.answer("Введите город или населенный пункт РФ для нового поиска.")
    await call.answer()


@router.callback_query(F.data == "nav:filters")
async def nav_filters(call: CallbackQuery) -> None:
    await call.message.answer("Открыл меню фильтров:", reply_markup=filters_root_kb())
    await call.answer()
