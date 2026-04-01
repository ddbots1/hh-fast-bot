from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.config import settings
from app.db.repository import UserRepository
from app.handlers.states import FilterInputState
from app.keyboards.filters import (
    age_kb,
    city_after_pick_kb,
    employment_kb,
    experience_kb,
    filters_root_kb,
    keyword_step_kb,
    salary_step_kb,
    schedule_kb,
)
from app.services.search import SearchService

router = Router()


@router.callback_query(F.data == "flt:city")
async def open_city(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(FilterInputState.waiting_city)
    await call.message.answer("Введи город или населенный пункт РФ (например: Москва, Тула, Мытищи).")
    await call.answer()


@router.callback_query(F.data == "flt:age")
async def open_age(call: CallbackQuery) -> None:
    await call.message.edit_text("Выбери возрастной фильтр:", reply_markup=age_kb())
    await call.answer()


@router.callback_query(F.data == "flt:employment")
async def open_employment(call: CallbackQuery) -> None:
    await call.message.edit_text("Выбери тип занятости:", reply_markup=employment_kb())
    await call.answer()


@router.callback_query(F.data == "flt:schedule")
async def open_schedule(call: CallbackQuery) -> None:
    await call.message.edit_text("Выбери график:", reply_markup=schedule_kb())
    await call.answer()


@router.callback_query(F.data == "flt:experience")
async def open_experience(call: CallbackQuery) -> None:
    await call.message.edit_text("Выбери опыт:", reply_markup=experience_kb())
    await call.answer()


@router.callback_query(F.data == "flt:salary")
async def open_salary(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(FilterInputState.waiting_salary)
    await call.message.answer(
        "Введи зарплату в формате `от` или `от-до` (пример: `150000` или `150000-300000`). Для сброса отправь `0`.",
        reply_markup=salary_step_kb(),
    )
    await call.answer()


@router.callback_query(F.data == "flt:text_hint")
async def open_text_hint(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(FilterInputState.waiting_text)
    await call.message.answer(
        "Введи ключевые слова для поиска (например: Python FastAPI удаленно) или пропусти этот шаг.",
        reply_markup=keyword_step_kb(),
    )
    await call.answer()


@router.callback_query(F.data == "flt:skip_text")
async def skip_text_filter(call: CallbackQuery, state: FSMContext, user_repo: UserRepository) -> None:
    filters = await user_repo.get_filters(call.from_user.id)
    filters.text = ""
    await user_repo.save_filters(call.from_user.id, filters)
    await state.clear()
    await call.message.answer("✅ Ключевые слова пропущены.")
    await call.message.answer("Нажми *«🔎 Показать вакансии»*.", reply_markup=keyword_step_kb())
    await call.answer("Пропущено")


@router.callback_query(F.data == "flt:skip_salary")
async def skip_salary_filter(call: CallbackQuery, state: FSMContext, user_repo: UserRepository) -> None:
    filters = await user_repo.get_filters(call.from_user.id)
    filters.salary_from = ""
    filters.salary_to = ""
    await user_repo.save_filters(call.from_user.id, filters)
    await state.set_state(FilterInputState.waiting_text)
    await call.message.answer(
        "✅ Шаг зарплаты пропущен. Можешь ввести ключевые слова или сразу показать вакансии.",
        reply_markup=keyword_step_kb(),
    )
    await call.answer("Пропущено")


@router.callback_query(F.data == "flt:back_filters")
async def back_to_filters(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.answer("Возвращаю меню фильтров.", reply_markup=filters_root_kb())
    await call.answer()


@router.callback_query(F.data.startswith("set:age:"))
async def set_age(call: CallbackQuery, user_repo: UserRepository) -> None:
    value = call.data.replace("set:age:", "", 1)
    filters = await user_repo.get_filters(call.from_user.id)
    filters.age_from = value
    await user_repo.save_filters(call.from_user.id, filters)
    await call.answer("Возраст сохранен")
    await call.message.edit_text(
        "✅ Возраст сохранен. Следующий шаг: выбери *тип занятости*.",
        reply_markup=employment_kb(),
    )


@router.callback_query(F.data.startswith("set:employment:"))
async def set_employment(call: CallbackQuery, user_repo: UserRepository) -> None:
    value = call.data.replace("set:employment:", "", 1)
    filters = await user_repo.get_filters(call.from_user.id)
    filters.employment = value
    await user_repo.save_filters(call.from_user.id, filters)
    await call.answer("Занятость сохранена")
    await call.message.edit_text(
        "✅ Занятость сохранена. Следующий шаг: выбери *график*.",
        reply_markup=schedule_kb(),
    )


@router.callback_query(F.data.startswith("set:schedule:"))
async def set_schedule(call: CallbackQuery, user_repo: UserRepository) -> None:
    value = call.data.replace("set:schedule:", "", 1)
    filters = await user_repo.get_filters(call.from_user.id)
    filters.schedule = value
    await user_repo.save_filters(call.from_user.id, filters)
    await call.answer("График сохранен")
    await call.message.edit_text(
        "✅ График сохранен. Следующий шаг: выбери *опыт*.",
        reply_markup=experience_kb(),
    )


@router.callback_query(F.data.startswith("set:experience:"))
async def set_experience(call: CallbackQuery, state: FSMContext, user_repo: UserRepository) -> None:
    value = call.data.replace("set:experience:", "", 1)
    filters = await user_repo.get_filters(call.from_user.id)
    filters.experience = value
    await user_repo.save_filters(call.from_user.id, filters)
    await state.set_state(FilterInputState.waiting_salary)
    await call.answer("Опыт сохранен")
    await call.message.edit_text(
        "✅ Опыт сохранен. Следующий шаг: укажи *зарплату* (например `150000` или `150000-300000`)."
    )


@router.message(FilterInputState.waiting_text)
async def set_text_filter(message: Message, state: FSMContext, user_repo: UserRepository) -> None:
    filters = await user_repo.get_filters(message.from_user.id)
    filters.text = message.text.strip()
    await user_repo.save_filters(message.from_user.id, filters)
    await state.clear()
    await message.answer("✅ Ключевые слова сохранены.")
    await message.answer("Финальный шаг: нажми *«🔎 Показать вакансии»*.", reply_markup=keyword_step_kb())


@router.message(FilterInputState.waiting_salary)
async def set_salary_filter(message: Message, state: FSMContext, user_repo: UserRepository) -> None:
    value = message.text.strip()
    filters = await user_repo.get_filters(message.from_user.id)
    if value == "0":
        filters.salary_from = ""
        filters.salary_to = ""
    elif "-" in value:
        salary_from, salary_to = value.split("-", maxsplit=1)
        filters.salary_from = salary_from.strip()
        filters.salary_to = salary_to.strip()
    else:
        filters.salary_from = value
        filters.salary_to = ""
    await user_repo.save_filters(message.from_user.id, filters)
    await state.clear()
    await message.answer("✅ Фильтр зарплаты сохранен.")
    await state.set_state(FilterInputState.waiting_text)
    await message.answer(
        "Следующий шаг: введи *ключевые слова* (например: Python, удаленно, FastAPI) или пропусти.",
        reply_markup=keyword_step_kb(),
    )


@router.message(FilterInputState.waiting_city)
async def set_city_from_text(
    message: Message, state: FSMContext, search_service: SearchService, user_repo: UserRepository
) -> None:
    query = message.text.strip()
    matches = await search_service.hh_client.search_ru_areas(query, limit=15)
    if not matches:
        await message.answer("Не нашел такой город в РФ. Попробуй другое название.")
        return

    exact = next(
        (
            item
            for item in matches
            if item["name"].lower() == query.lower()
            or item.get("display_name", "").lower() == query.lower()
        ),
        None,
    )
    if exact:
        filters = await user_repo.get_filters(message.from_user.id)
        filters.city_area_id = exact["id"]
        filters.city_name = exact["name"]
        filters.page = 0
        await user_repo.save_filters(message.from_user.id, filters)
        await state.clear()
        await message.answer(f"Город установлен: *{exact['name']}*")
        await message.answer(
            "Выбери режим: быстрый поиск сразу или детальная настройка фильтров.",
            reply_markup=city_after_pick_kb(),
        )
        return

    await state.update_data(city_candidates=matches)
    await state.set_state(FilterInputState.waiting_city_pick)
    variants = "\n".join(
        f"{idx + 1}. {item.get('display_name', item['name'])}"
        for idx, item in enumerate(matches)
    )
    await message.answer(f"Уточни город — отправь номер варианта:\n{variants}")


@router.message(FilterInputState.waiting_city_pick)
async def set_city_from_pick(message: Message, state: FSMContext, user_repo: UserRepository) -> None:
    if not message.text.isdigit():
        await message.answer("Отправь только номер варианта цифрой.")
        return
    idx = int(message.text) - 1
    data = await state.get_data()
    candidates = data.get("city_candidates", [])
    if idx < 0 or idx >= len(candidates):
        await message.answer("Неверный номер. Выбери из списка.")
        return
    selected = candidates[idx]
    filters = await user_repo.get_filters(message.from_user.id)
    filters.city_area_id = selected["id"]
    filters.city_name = selected["name"]
    filters.page = 0
    await user_repo.save_filters(message.from_user.id, filters)
    await state.clear()
    await message.answer(f"Город установлен: *{selected['name']}*")
    await message.answer(
        "Выбери режим: быстрый поиск сразу или детальная настройка фильтров.",
        reply_markup=city_after_pick_kb(),
    )
