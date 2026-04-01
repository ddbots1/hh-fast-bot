"""
Обработчик поиска вакансий и отправки результатов
"""

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from loguru import logger
from typing import List

from hh_service import hh_service
from cache_service import cache_service
from db_service import db_service
from formatter import FormatterService
from search_keyboards import SearchKeyboards
from partners_config import get_partner_vacancy
from models import Vacancy


router = Router()


@router.callback_query(F.data == "search_execute")
async def execute_search(callback: types.CallbackQuery, state: FSMContext):
    """Выполнить поиск вакансий"""
    
    data = await state.get_data()
    filters = data.get("filters", {})
    user_id = callback.from_user.id
    
    await callback.answer("🔍 Ищу вакансии...", show_alert=False)
    
    try:
        # Показываем статус
        await callback.message.edit_text(
            "⏳ Ищу вакансии на HH.ru...",
            parse_mode="Markdown"
        )
        
        # Получаем вакансии с HH.ru API
        logger.info(f"🔍 Поиск вакансий для пользователя {user_id}")
        
        vacancies = await hh_service.get_vacancies_parsed(
            text=filters.get("text"),
            area=filters.get("area_id"),
            experience=filters.get("experience"),
            employment=filters.get("employment"),
            schedule=filters.get("schedule"),
            salary_from=filters.get("salary_from"),
            salary_to=filters.get("salary_to"),
            page=0,
            per_page=10,
            accept_kids=filters.get("accept_kids", False)
        )
        
        if not vacancies:
            logger.warning(f"⚠️ Вакансии не найдены для {user_id}")
            
            await callback.message.edit_text(
                FormatterService.format_no_results(),
                reply_markup=SearchKeyboards.back_button(),
                parse_mode="Markdown"
            )
            return
        
        # Сохраняем результаты в кэш
        cache_key = f"search_{user_id}_{hash(str(filters))}"
        vacancies_data = [v.to_dict() for v in vacancies]
        await cache_service.cache_search_results(cache_key, vacancies_data)
        
        # Сохраняем в FSM для пагинации
        await state.update_data(
            search_results=vacancies_data,
            current_page=0,
            cache_key=cache_key,
            total_vacancies=len(vacancies)
        )
        
        # Сохраняем в историю поиска
        await db_service.add_search_history(
            user_id,
            str(filters),
            len(vacancies)
        )
        
        logger.success(f"✅ Найдено {len(vacancies)} вакансий для пользователя {user_id}")
        
        # Показываем первую страницу результатов
        await show_vacancies_page(callback, state, page=0)
    
    except Exception as e:
        logger.error(f"❌ Ошибка при поиске: {e}")
        
        await callback.message.edit_text(
            FormatterService.format_error(),
            reply_markup=SearchKeyboards.back_button(),
            parse_mode="Markdown"
        )


async def show_vacancies_page(callback: types.CallbackQuery, state: FSMContext, page: int = 0):
    """Показать страницу с вакансиями (3 штуки)"""
    
    try:
        data = await state.get_data()
        search_results = data.get("search_results", [])
        user_id = callback.from_user.id
        city = data.get("filters", {}).get("area_name", "default")
        
        # Получаем вакансии для этой страницы
        start_idx = page * 3
        end_idx = start_idx + 2
        
        vacancies_for_page = search_results[start_idx:end_idx]
        
        if not vacancies_for_page:
            text = "😔 Больше вакансий нет"
            await callback.message.edit_text(
                text,
                reply_markup=SearchKeyboards.back_button(),
                parse_mode="Markdown"
            )
            return
        
        # Получаем партнёрскую вакансию для этого города и страницы
        partner_vacancy = get_partner_vacancy(city, page=page)
        
        # Преобразуем dict обратно в Vacancy объекты
        vacancies = []
        for v_dict in vacancies_for_page:
            from models import Vacancy, Salary, Area
            
            salary = None
            if v_dict.get("salary", {}).get("from") or v_dict.get("salary", {}).get("to"):
                salary = Salary(
                    from_amount=v_dict["salary"].get("from"),
                    to_amount=v_dict["salary"].get("to")
                )
            
            area = Area(id=0, name=v_dict.get("area", ""))
            
            vacancy = Vacancy(
                id=v_dict.get("id", ""),
                name=v_dict.get("name", ""),
                url=v_dict.get("url", ""),
                salary=salary,
                area=area,
                employer_name=v_dict.get("employer", ""),
                snippet_responsibility=v_dict.get("description", ""),
            )
            vacancies.append(vacancy)
        
        # Форматируем вакансии с партнёркой
        text = FormatterService.format_vacancies_pack(
            vacancies,
            partner_vacancy=partner_vacancy,
            page=page
        )
        
        # Проверяем есть ли следующая страница
        has_next = (start_idx + 3) < len(search_results)
        
        # Отправляем с пагинацией
        await callback.message.edit_text(
            text,
            reply_markup=SearchKeyboards.pagination(page, has_next),
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
        
        await state.update_data(current_page=page)
        logger.info(f"📄 Показана страница {page} для пользователя {user_id}")
    
    except Exception as e:
        logger.error(f"❌ Ошибка при показе страницы: {e}")
        await callback.answer("❌ Ошибка при загрузке страницы", show_alert=True)


@router.callback_query(F.data.startswith("page_"))
async def page_navigation(callback: types.CallbackQuery, state: FSMContext):
    """Навигация по страницам"""
    
    page = int(callback.data.split("_")[1])
    await show_vacancies_page(callback, state, page=page)
    await callback.answer()


@router.callback_query(F.data == "current_page")
async def show_current_page_info(callback: types.CallbackQuery, state: FSMContext):
    """Показать информацию текущей страницы"""
    
    data = await state.get_data()
    current_page = data.get("current_page", 0)
    total = data.get("total_vacancies", 0)
    
    text = f"""
📄 **Информация о странице**

Текущая страница: {current_page + 1}
Всего вакансий найдено: {total}
Вакансий на странице: 3 (1 партнёрская + 2 реальные)

📊 **Совет:** Используйте фильтры для более точного поиска!
"""
    
    await callback.answer(text, show_alert=True)


@router.callback_query(F.data == "add_to_favorites")
async def add_to_favorites(callback: types.CallbackQuery, state: FSMContext):
    """Добавить вакансию в избранное"""
    
    user_id = callback.from_user.id
    
    # Здесь нужно получить ID текущей вакансии из контекста
    # Это упрощённая версия
    
    await callback.answer("⭐ Добавлено в избранное!", show_alert=False)
    logger.info(f"⭐ Вакансия добавлена в избранное пользователю {user_id}")


@router.callback_query(F.data == "next_vacancy")
async def next_vacancy(callback: types.CallbackQuery, state: FSMContext):
    """Перейти к следующей вакансии"""
    
    data = await state.get_data()
    current_page = data.get("current_page", 0)
    
    await show_vacancies_page(callback, state, page=current_page + 1)
    await callback.answer()
