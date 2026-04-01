import hashlib
import orjson
from typing import Any

from app.services.cache import CacheService
from app.services.hh_api import HHClient
from app.services.partner import PartnerService
from app.utils.constants import EMPLOYMENT_MAP, EXPERIENCE_MAP, SCHEDULE_MAP
from app.utils.formatters import format_salary


class SearchService:
    def __init__(self, hh_client: HHClient, cache: CacheService, partner_service: PartnerService) -> None:
        self.hh_client = hh_client
        self.cache = cache
        self.partner_service = partner_service

    @staticmethod
    def _cache_key(params: dict[str, Any]) -> str:
        packed = orjson.dumps(params, option=orjson.OPT_SORT_KEYS)
        return "hh:vac:" + hashlib.sha256(packed).hexdigest()

    async def get_partner(self, city_name: str) -> dict[str, str]:
        return self.partner_service.get_for_city(city_name)

    async def get_vacancies(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        salary_to = params.pop("salary_to", None)
        key = self._cache_key(params)
        cached = await self.cache.get(key)
        if cached is not None:
            return cached

        data = await self.hh_client.search_vacancies(params)
        items = data.get("items", [])
        result: list[dict[str, Any]] = []
        for item in items:
            result.append(
                {
                    "vacancy_id": item["id"],
                    "title": item["name"],
                    "employer": item.get("employer", {}).get("name", "Компания не указана"),
                    "salary": format_salary(item.get("salary")),
                    "city": item.get("area", {}).get("name", "Не указан"),
                    "employment": EMPLOYMENT_MAP.get(item.get("employment", {}).get("id", ""), ("Занятость не указана", ""))[0],
                    "schedule": SCHEDULE_MAP.get(item.get("schedule", {}).get("id", ""), ("График не указан", ""))[0],
                    "experience": EXPERIENCE_MAP.get(item.get("experience", {}).get("id", ""), ("Опыт не указан", ""))[0],
                    "skills": [s["name"] for s in item.get("key_skills", [])] if item.get("key_skills") else [],
                    "url": item["alternate_url"],
                }
            )

        if salary_to:
            max_salary = int(salary_to)
            filtered: list[dict[str, Any]] = []
            for item in result:
                text_salary = item["salary"]
                digits = "".join(ch if ch.isdigit() else " " for ch in text_salary)
                parts = [int(x) for x in digits.split() if x.isdigit()]
                if not parts or min(parts) <= max_salary:
                    filtered.append(item)
            result = filtered

        await self.cache.set(key, result, ttl=60)
        return result
