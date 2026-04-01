# HH Fast Bot

Асинхронный Telegram-бот на `aiogram 3.x` для быстрого поиска вакансий с `hh.ru`.

## Архитектура

- `main.py` — точка входа, инициализация зависимостей, middleware, polling.
- `app/config.py` — настройки из `.env`.
- `app/handlers/` — команды, меню, фильтры, поиск, избранное.
- `app/services/` — интеграции: HH API, кэш (Redis/in-memory), партнерки, статистика.
- `app/db/` — SQLite-слой для пользователей, фильтров, избранного.
- `app/keyboards/` — Reply/Inline-клавиатуры.
- `app/middlewares/antiflood.py` — защита от спама.
- `app/utils/` — константы фильтров и форматирование карточек вакансий.

## Запуск

1. Установите Python 3.11+.
2. Установите зависимости:
   - `pip install -r requirements.txt`
3. Скопируйте `.env.example` в `.env` и заполните:
   - `BOT_TOKEN`
   - `REDIS_URL` (если Redis используете)
4. Запуск:
   - `python main.py`

## Примечания

- Если Redis недоступен, установите `USE_REDIS=false` — включится in-memory cache.
- Партнерки редактируются в `app/services/partner.py`.
- На каждый поиск: 1 карточка партнерки + 7 реальных вакансий HH.
