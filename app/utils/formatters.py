from typing import Any


def format_salary(salary: Any) -> str:
    if not salary:
        return "Зарплата не указана"
    
    # Если это уже строка (например, из кэша)
    if isinstance(salary, str):
        return salary

    # Если это словарь от HH.ru API
    if isinstance(salary, dict):
        s_from = salary.get("from")
        s_to = salary.get("to")
        currency = salary.get("currency", "RUR")
        
        # Замена валюты на символ
        currency_map = {"RUR": "₽", "USD": "$", "EUR": "€", "BYR": "Br", "KZT": "₸"}
        cur_sym = currency_map.get(currency, currency)

        if s_from and s_to:
            return f"{s_from:,} — {s_to:,} {cur_sym}".replace(",", " ")
        if s_from:
            return f"от {s_from:,} {cur_sym}".replace(",", " ")
        if s_to:
            return f"до {s_to:,} {cur_sym}".replace(",", " ")
    
    return "Зарплата не указана"


def format_vacancy_text(item: dict[str, Any]) -> str:
    skills = " • ".join(item.get("skills", [])[:4])
    skills_text = f"\n\n🧠 `{skills}`" if skills else ""
    
    return (
        f"🚀 *{item['title']}*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 {item['salary']}\n"
        f"🏢 {item.get('employer', 'Компания не указана')}\n"
        f"📍 {item['city']}\n\n"
        f"⏳ {item['experience']} • {item['schedule']}{skills_text}"
    )


def format_partner_text(item: dict[str, str]) -> str:
    return (
        f"⭐ *{item['title']}* — _РЕКОМЕНДУЕМ_\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💸 {item['salary']}\n"
        f"📍 {item['city']}\n\n"
        f"📝 {item['description']}\n\n"
        f"⚡ {item['emoji']} {item.get('employment', 'Быстрый отклик')}"
    )
