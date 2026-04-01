"""
Обработчик команды /start и главного меню
"""

from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from loguru import logger

from config import settings
from search_keyboards import SearchKeyboards
from db_service import db_service
from formatter import FormatterService


router = Router()


@router.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    """Команда /start - приветствие и главное меню"""
    
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""
    
    logger.info(f"👤 Новый/возврат пользователя: {user_id} (@{username})")
    
    # Сохраняем пользователя в БД
    await db_service.add_user(user_id, username, first_name, last_name)
    
    # Очищаем FSM состояние
    await state.clear()
    
    # Приветственное сообщение
    welcome_text = """
🔥 **HH Fast** — самый быстрый HR-бот для поиска вакансий!

⚡ Ищи вакансии молниеносно
💼 Все фильтры как на HH.ru
⭐ Сохраняй избранные вакансии
🌍 Работа по всей России

👇 Начни поиск прямо сейчас:
"""
    
    await message.answer(
        welcome_text,
        reply_markup=SearchKeyboards.main_menu(),
        parse_mode="Markdown"
    )
    
    logger.success(f"✅ Приветствие отправлено пользователю {user_id}")


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    """Вернуться в главное меню"""
    
    await state.clear()
    
    menu_text = """
🏠 **Главное меню**

Выберите действие:
"""
    
    await callback.message.edit_text(
        menu_text,
        reply_markup=SearchKeyboards.main_menu(),
        parse_mode="Markdown"
    )
    
    await callback.answer()


@router.callback_query(F.data == "search_start")
async def search_start(callback: types.CallbackQuery, state: FSMContext):
    """Начало поиска - выбор параметров"""
    
    user_id = callback.from_user.id
    logger.info(f"🔍 Пользователь {user_id} начал новый поиск")
    
    # Инициализируем фильтры в FSM
    await state.set_data({
        "filters": {
            "text": None,
            "area_id": None,
            "area_name": None,
            "experience": None,
            "employment": None,
            "schedule": None,
            "salary_from": None,
            "salary_to": None,
            "only_with_salary": False,
            "only_direct_employer": False,
            "last_24_hours": False,
            "for_disabled": False,
            "accept_kids": False,
        },
        "page": 0
    })
    
    search_text = """
🔍 **Новый поиск**

Введите должность или ключевые слова.
Например: "Python", "Курьер", "Маркетолог"

Или используйте кнопки ниже для быстрого фильтра:
"""
    
    keyboard = SearchKeyboards.main_menu()
    
    await callback.message.edit_text(
        search_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    
    await callback.answer()


@router.callback_query(F.data == "my_filters")
async def my_filters(callback: types.CallbackQuery):
    """Показать сохранённые фильтры пользователя"""
    
    user_id = callback.from_user.id
    filters = await db_service.get_user_filters(user_id)
    
    if not filters:
        text = """
📋 **Сохранённые фильтры**

У вас пока нет сохранённых фильтров.

Создайте новый поиск и сохраните фильтры! 💾
"""
    else:
        text = "📋 **Сохранённые фильтры**\n\n"
        
        for i, f in enumerate(filters[:5], 1):  # Показываем максимум 5
            filter_name = f['filter_name'] or f"Поиск {i}"
            text += f"{i}. {filter_name}\n"
        
        if len(filters) > 5:
            text += f"\n... и ещё {len(filters) - 5}\n"
        
        text += "\n💡 Выберите или создайте новый поиск"
    
    await callback.message.edit_text(
        text,
        reply_markup=SearchKeyboards.back_button(),
        parse_mode="Markdown"
    )
    
    await callback.answer()


@router.callback_query(F.data == "about")
async def about_bot(callback: types.CallbackQuery):
    """Информация о боте"""
    
    about_text = """
ℹ️ **Об HH Fast**

**Версия:** 1.0.0
**Статус:** ✅ Активен и работает

**Возможности:**
🔍 Поиск вакансий на HH.ru
💾 Сохранение фильтров
⭐ Избранные вакансии
📊 История поисков
🚀 Быстрый поиск (< 2 сек)

**Автор:** @maxdev
**Поддержка:** @support

Спасибо за использование бота! 🙏
"""
    
    await callback.message.edit_text(
        about_text,
        reply_markup=SearchKeyboards.back_button(),
        parse_mode="Markdown"
    )
    
    await callback.answer()


@router.callback_query(F.data == "settings")
async def settings(callback: types.CallbackQuery):
    """Настройки бота"""
    
    settings_text = """
⚙️ **Настройки**

🔔 Уведомления: ✅ Включены
📱 Язык: 🇷🇺 Русский
💬 Подробный поиск: ✅ Да

Больше настроек скоро появится! 🚀
"""
    
    await callback.message.edit_text(
        settings_text,
        reply_markup=SearchKeyboards.back_button(),
        parse_mode="Markdown"
    )
    
    await callback.answer()


@router.message(Command("help"))
async def help_command(message: types.Message):
    """Справка по командам"""
    
    help_text = """
📚 **Справка по командам**

**/start** - главное меню
**/help** - эта справка
**/search** - быстрый поиск
**/favorites** - избранное
**/history** - история поисков

📖 Для детальной справки нажми кнопку ниже 👇
"""
    
    await message.answer(
        help_text,
        reply_markup=SearchKeyboards.back_button(),
        parse_mode="Markdown"
    )
