PARTNER_LINKS = [
    "https://trk.ppdu.ru/click/9sMgPQp7?erid=2SDnjcbs16H",
    "https://trk.ppdu.ru/click/fuTVHjv6?erid=Kra23uVC3",
    "https://trk.ppdu.ru/click/NpSXV648?erid=2SDnjeL6Zwp",
    "https://trk.ppdu.ru/click/NpSXV648?erid=2SDnjeL6Zwp&landingId=100",
    "https://trk.ppdu.ru/click/NpSXV648?erid=2SDnjeL6Zwp&landingId=101",
    "https://trk.ppdu.ru/click/NpSXV648?erid=2SDnjeL6Zwp&landingId=906",
]

PARTNER_TEMPLATES = [
    {
        "title": "Пеший курьер в Купер",
        "salary": "до 243 000 ₽ в месяц",
        "description": "Свободный график, район на выбор, выплаты каждую неделю и бонусы за рекомендации.",
        "emoji": "🛴",
        "employment": "Частичная или полная занятость",
        "schedule": "Гибкий / смены от нескольких часов",
        "experience": "Без опыта, с 18+",
        "button_text": "🚀 Начать в Купер",
    },
    {
        "title": "Велокурьер в сервис доставки",
        "salary": "до 220 000 ₽ в месяц",
        "description": "Доставляйте рядом с домом, получайте чаевые и скидки от партнеров.",
        "emoji": "🚲",
        "employment": "Подработка или full-time",
        "schedule": "Гибкий, сами выбираете слоты",
        "experience": "Подойдет новичкам",
        "button_text": "⚡ Хочу на велодоставку",
    },
    {
        "title": "Водитель-курьер",
        "salary": "до 260 000 ₽ в месяц",
        "description": "Понятный старт, поддержка, стабильный поток заказов и быстрый выход на доход.",
        "emoji": "🚗",
        "employment": "Проектная / полная занятость",
        "schedule": "Сменный или гибкий",
        "experience": "С опытом и без",
        "button_text": "💼 Перейти к вакансии",
    },
    {
        "title": "Сборщик заказов",
        "salary": "до 180 000 ₽ в месяц",
        "description": "Комфортная работа в магазине, понятные задачи и регулярные выплаты.",
        "emoji": "🛒",
        "employment": "Частичная или полная занятость",
        "schedule": "Гибкий или сменный",
        "experience": "Без опыта",
        "button_text": "✨ Откликнуться сейчас",
    },
]


class PartnerService:
    def get_for_city(self, city: str) -> dict[str, str]:
        city_name = city or "Ваш город"
        idx = abs(hash(city_name)) % len(PARTNER_TEMPLATES)
        data = PARTNER_TEMPLATES[idx].copy()
        data["url"] = PARTNER_LINKS[idx % len(PARTNER_LINKS)]
        data["city"] = city_name
        return data
