"""
Обработчик фильтров поиска (город, опыт, занятость, график и т.д.)
"""

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from loguru import logger

from search_keyboards import SearchKeyboards
from cache_service import cache_service
from db_service import db_service


router = Router()


# ============ ФИЛЬТР: ГОРОД ============

@router.callback_query(F.data.startswith("city_"))
async def select_city(callback: types.CallbackQuery, state: FSMContext):
    """Выбор города из популярных"""
    
    city_id = int(callback.data.split("_")[1])
    
    # Получаем название города из callback data
    city_names = {
        1: "Москва", 2: "Санкт-Петербург", 3: "Новосибирск",
        4: "Екатеринбург", 5: "Казань", 6: "Пермь",
        8: "Воронеж", 33: "Тюмень", 53: "Краснодар", 104: "Омск"
    }
    
    city_name = city_names.get(city_id, f"Город ID {city_id}")
    
    # Сохраняем в FSM
    data = await state.get_data()
    filters = data.get("filters", {})
    filters["area_id"] = city_id
    filters["area_name"] = city_name
    
    await state.update_data(filters=filters)
    
    logger.info(f"🌍 Выбран город: {city_name} (ID: {city_id})")
    
    # Показываем следующий фильтр
    await show_experience_filter(callback, state)


async def show_experience_filter(callback: types.CallbackQuery, state: FSMContext):
    """Показать фильтр опыта"""
    
    data = await state.get_data()
    filters = data.get("filters", {})
    city_name = filters.get("area_name", "Выбранный город")
    
    text = f"""
✅ Город выбран: **{city_name}**

👤 **Опыт работы**

Какой опыт требуется?
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=SearchKeyboards.experience_menu(),
        parse_mode="Markdown"
    )


# ============ ФИЛЬТР: ОПЫТ ============

@router.callback_query(F.data.startswith("exp_"))
async def select_experience(callback: types.CallbackQuery, state: FSMContext):
    """Выбор опыта"""
    
    exp_code = callback.data.replace("exp_", "")
    
    if exp_code != "skip":
        # Сохраняем в FSM
        data = await state.get_data()
        filters = data.get("filters", {})
        filters["experience"] = exp_code
        await state.update_data(filters=filters)
        
        logger.info(f"📚 Выбран опыт: {exp_code}")
    
    # Показываем следующий фильтр
    await show_employment_filter(callback, state)


async def show_employment_filter(callback: types.CallbackQuery, state: FSMContext):
    """Показать фильтр занятости"""
    
    data = await state.get_data()
    filters = data.get("filters", {})
    
    text = """
🕒 **Занятость**

Какой тип занятости вас интересует?
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=SearchKeyboards.employment_menu(),
        parse_mode="Markdown"
    )


# ============ ФИЛЬТР: ЗАНЯТОСТЬ ============

@router.callback_query(F.data.startswith("emp_"))
async def select_employment(callback: types.CallbackQuery, state: FSMContext):
    """Выбор занятости"""
    
    emp_code = callback.data.replace("emp_", "")
    
    if emp_code != "skip":
        data = await state.get_data()
        filters = data.get("filters", {})
        filters["employment"] = emp_code
        await state.update_data(filters=filters)
        
        logger.info(f"💼 Выбрана занятость: {emp_code}")
    
    # Показываем следующий фильтр
    await show_schedule_filter(callback, state)


async def show_schedule_filter(callback: types.CallbackQuery, state: FSMContext):
    """Показать фильтр графика"""
    
    text = """
🗓️ **График работы**

Какой график вас интересует?
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=SearchKeyboards.schedule_menu(),
        parse_mode="Markdown"
    )


# ============ ФИЛЬТР: ГРАФИК ============

@router.callback_query(F.data.startswith("sch_"))
async def select_schedule(callback: types.CallbackQuery, state: FSMContext):
    """Выбор графика"""
    
    sch_code = callback.data.replace("sch_", "")
    
    if sch_code != "skip":
        data = await state.get_data()
        filters = data.get("filters", {})
        filters["schedule"] = sch_code
        await state.update_data(filters=filters)
        
        logger.info(f"📅 Выбран график: {sch_code}")
    
    # Показываем специальные фильтры
    await show_special_filters(callback, state)


async def show_special_filters(callback: types.CallbackQuery, state: FSMContext):
    """Показать специальные фильтры"""
    
    text = """
⚙️ **Дополнительные фильтры**

Выберите специальные условия (опционально):
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=SearchKeyboards.special_filters_menu(),
        parse_mode="Markdown"
    )


# ============ СПЕЦИАЛЬНЫЕ ФИЛЬТРЫ ============

@router.callback_query(F.data == "filter_with_salary")
async def toggle_with_salary(callback: types.CallbackQuery, state: FSMContext):
    """Фильтр: только вакансии с зарплатой"""
    
    data = await state.get_data()
    filters = data.get("filters", {})
    filters["only_with_salary"] = not filters.get("only_with_salary", False)
    
    await state.update_data(filters=filters)
    logger.info(f"💰 Фильтр зарплаты: {filters['only_with_salary']}")
    
    await show_special_filters(callback, state)
    await callback.answer("✅ Фильтр обновлён", show_alert=False)


@router.callback_query(F.data == "filter_direct_employer")
async def toggle_direct_employer(callback: types.CallbackQuery, state: FSMContext):
    """Фильтр: только прямые работодатели"""
    
    data = await state.get_data()
    filters = data.get("filters", {})
    filters["only_direct_employer"] = not filters.get("only_direct_employer", False)
    
    await state.update_data(filters=filters)
    logger.info(f"🏢 Фильтр прямых работодателей: {filters['only_direct_employer']}")
    
    await show_special_filters(callback, state)
    await callback.answer("✅ Фильтр обновлён", show_alert=False)


@router.callback_query(F.data == "filter_last_24h")
async def toggle_last_24h(callback: types.CallbackQuery, state: FSMContext):
    """Фильтр: вакансии за последние 24 часа"""
    
    data = await state.get_data()
    filters = data.get("filters", {})
    filters["last_24_hours"] = not filters.get("last_24_hours", False)
    
    await state.update_data(filters=filters)
    logger.info(f"⏰ Фильтр 24 часа: {filters['last_24_hours']}")
    
    await show_special_filters(callback, state)
    await callback.answer("✅ Фильтр обновлён", show_alert=False)


@router.callback_query(F.data == "filter_disabled")
async def toggle_for_disabled(callback: types.CallbackQuery, state: FSMContext):
    """Фильтр: вакансии для людей с инвалидностью"""
    
    data = await state.get_data()
    filters = data.get("filters", {})
    filters["for_disabled"] = not filters.get("for_disabled", False)
    
    await state.update_data(filters=filters)
    logger.info(f"♿ Фильтр для инвалидов: {filters['for_disabled']}")
    
    await show_special_filters(callback, state)
    await callback.answer("✅ Фильтр обновлён", show_alert=False)


@router.callback_query(F.data == "filter_kids")
async def toggle_for_kids(callback: types.CallbackQuery, state: FSMContext):
    """Фильтр: вакансии для подростков (до 18 лет)"""
    
    data = await state.get_data()
    filters = data.get("filters", {})
    filters["accept_kids"] = not filters.get("accept_kids", False)
    
    if filters["accept_kids"]:
        # Автоматически ставим "Без опыта" для подростков
        filters["experience"] = "noExperience"
    
    await state.update_data(filters=filters)
    logger.info(f"👶 Фильтр для подростков: {filters['accept_kids']}")
    
    await show_special_filters(callback, state)
    await callback.answer("✅ Фильтр для подростков активирован!", show_alert=True)


@router.callback_query(F.data == "search_execute")
async def execute_search(callback: types.CallbackQuery, state: FSMContext):
    """Выполнить поиск"""
    
    data = await state.get_data()
    filters = data.get("filters", {})
    user_id = callback.from_user.id
    
    logger.info(f"🔍 Запуск поиска для пользователя {user_id} с фильтрами: {filters}")
    
    await callback.answer("🔍 Ищу вакансии...", show_alert=False)
    
    # Здесь будет выполнение поиска в search.py
    # Пока просто переходим на страницу результатов
    await callback.message.edit_text(
        "⏳ Ищу вакансии...",
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "back_to_filters")
async def back_to_filters(callback: types.CallbackQuery, state: FSMContext):
    """Вернуться к фильтрам"""
    
    await state.clear()
    
    text = "🔙 Возврат в меню"
    
    await callback.message.edit_text(
        text,
        reply_markup=SearchKeyboards.main_menu(),
        parse_mode="Markdown"
    )
    
    await callback.answer()
