"""
Партнёрские вакансии - конфиг для размещения рекламы
Легко заменяешь на реальные ссылки и данные
"""

PARTNER_VACANCIES = {
    "Москва": [
        {
            "emoji": "🍔",
            "title": "Курьер на скутере",
            "salary": "200 000 — 300 000 ₽",
            "schedule": "Полная занятость • Москва",
            "description": "Срочно ищем курьеров на скутерах для доставки еды. Работай сам себе босс, зарабатывай по графику!",
            "button_text": "Хочу попробовать →",
            "url": "https://example.com/partner1"
        },
        {
            "emoji": "💼",
            "title": "Менеджер по продажам",
            "salary": "150 000 — 250 000 ₽",
            "schedule": "Полная занятость • Москва",
            "description": "Растущая компания ищет амбициозного менеджера. Без опыта берём! Обучаем с нуля.",
            "button_text": "Узнать больше →",
            "url": "https://example.com/partner2"
        },
    ],
    
    "Санкт-Петербург": [
        {
            "emoji": "🏪",
            "title": "Продавец-консультант",
            "salary": "35 000 — 50 000 ₽",
            "schedule": "Полная занятость • СПб",
            "description": "Элитный мебельный салон ищет консультантов. Уютная работа, высокие комиссии!",
            "button_text": "Работать здесь →",
            "url": "https://example.com/partner3"
        },
    ],
    
    "Казань": [
        {
            "emoji": "👨‍💻",
            "title": "Junior Python разработчик",
            "salary": "80 000 — 120 000 ₽",
            "schedule": "Полная занятость • Казань",
            "description": "IT стартап ищет junior программиста на Python. Менторство, обучение, перспективы!",
            "button_text": "Присоединиться →",
            "url": "https://example.com/partner4"
        },
    ],
    
    "default": [
        {
            "emoji": "🎁",
            "title": "Работа онлайн для каждого",
            "salary": "Гибкая зарплата",
            "schedule": "Удалённая работа • По всей России",
            "description": "Ищешь работу? На нашей платформе 1000+ вакансий в день. Исполнители, фрилансеры, удалёнка - всё тут!",
            "button_text": "Найти работу →",
            "url": "https://example.com/default"
        },
    ]
}


def get_partner_vacancy(city: str, page: int = 0):
    """
    Получить партнёрскую вакансию для города
    
    Args:
        city: название города или ID
        page: номер страницы (для циклического показа разных вакансий)
    
    Returns:
        dict: партнёрская вакансия
    """
    
    # Получаем список вакансий для города
    vacancies = PARTNER_VACANCIES.get(city, PARTNER_VACANCIES.get("default", []))
    
    if not vacancies:
        vacancies = PARTNER_VACANCIES["default"]
    
    # Циклически выбираем вакансию по номеру страницы
    index = page % len(vacancies)
    return vacancies[index]


# Примеры использования:
# partner = get_partner_vacancy("Москва", page=0)
# partner["title"] → "Курьер на скутере"
