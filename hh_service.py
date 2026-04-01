"""
Сервис для взаимодействия с HH.ru API
Делает поиск вакансий, парсит результаты
"""

import httpx
from typing import List, Optional, Dict
from loguru import logger

from config import settings
from models import Vacancy, Salary, Area


class HHService:
    """Сервис для работы с HH.ru API"""
    
    def __init__(self):
        self.base_url = settings.HH_API_BASE
        self.timeout = httpx.Timeout(settings.HH_REQUEST_TIMEOUT)
        self.headers = {
            "User-Agent": "HH Fast Bot (Python/aiogram)"
        }
    
    async def search_vacancies(
        self,
        text: Optional[str] = None,
        area: Optional[int] = None,
        experience: Optional[str] = None,
        employment: Optional[str] = None,
        schedule: Optional[str] = None,
        salary_from: Optional[int] = None,
        salary_to: Optional[int] = None,
        page: int = 0,
        per_page: int = 20,
        **kwargs
    ) -> Dict:
        """
        Поиск вакансий на HH.ru
        
        Args:
            text: Ключевые слова для поиска
            area: ID города
            experience: Опыт (noExperience, between1And3, between3And6, moreThan6)
            employment: Занятость (full, part, project, probation)
            schedule: График (fullDay, shift, flexible, remote, flyInFlyOut)
            salary_from: Зарплата от
            salary_to: Зарплата до
            page: Номер страницы
            per_page: Вакансий на странице
        
        Returns:
            Dict с вакансиями
        """
        
        params = {
            "page": page,
            "per_page": per_page,
        }
        
        # Добавляем параметры если указаны
        if text:
            params["text"] = text
        if area:
            params["area"] = area
        if experience:
            params["experience"] = experience
        if employment:
            params["employment"] = employment
        if schedule:
            params["schedule"] = schedule
        if salary_from:
            params["salary_from"] = salary_from
        if salary_to:
            params["salary_to"] = salary_to
        
        # Специальный флаг для подростков (до 18 лет)
        if kwargs.get("accept_kids"):
            params["label"] = "accept_kids"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/vacancies",
                    params=params,
                    headers=self.headers
                )
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"✅ Найдено {data.get('found', 0)} вакансий")
                return data
        
        except httpx.TimeoutException:
            logger.error("⏱️ Timeout при запросе к HH.ru")
            return {"items": [], "found": 0}
        except httpx.RequestError as e:
            logger.error(f"❌ Ошибка запроса к HH.ru: {e}")
            return {"items": [], "found": 0}
    
    def parse_vacancy(self, item: dict) -> Vacancy:
        """Парсит вакансию из JSON ответа HH.ru"""
        
        # Зарплата
        salary = None
        if item.get("salary"):
            salary_data = item["salary"]
            salary = Salary(
                from_amount=salary_data.get("from"),
                to_amount=salary_data.get("to"),
                currency=salary_data.get("currency", "RUR")
            )
        
        # Город
        area = None
        if item.get("area"):
            area = Area(
                id=int(item["area"].get("id", 0)),
                name=item["area"].get("name", "")
            )
        
        # Работодатель
        employer_name = ""
        employer_logo = ""
        if item.get("employer"):
            employer_name = item["employer"].get("name", "")
            employer_logo = item["employer"].get("logo_urls", {}).get("original", "")
        
        vacancy = Vacancy(
            id=item.get("id", ""),
            name=item.get("name", ""),
            url=item.get("url", ""),
            alternate_url=item.get("alternate_url", ""),
            salary=salary,
            area=area,
            employer_name=employer_name,
            employer_logo_url=employer_logo,
            snippet_requirement=item.get("snippet", {}).get("requirement", ""),
            snippet_responsibility=item.get("snippet", {}).get("responsibility", ""),
            employment=item.get("employment"),
            schedule=item.get("schedule"),
            experience=item.get("experience"),
            published_at=item.get("published_at", ""),
            created_at=item.get("created_at", ""),
            response_letter_required=item.get("response_letter_required", False)
        )
        
        return vacancy
    
    async def get_vacancies_parsed(
        self,
        text: Optional[str] = None,
        area: Optional[int] = None,
        experience: Optional[str] = None,
        employment: Optional[str] = None,
        schedule: Optional[str] = None,
        salary_from: Optional[int] = None,
        salary_to: Optional[int] = None,
        page: int = 0,
        per_page: int = 20,
        **kwargs
    ) -> List[Vacancy]:
        """
        Поиск вакансий и парсинг результатов
        
        Returns:
            Список объектов Vacancy
        """
        
        data = await self.search_vacancies(
            text=text,
            area=area,
            experience=experience,
            employment=employment,
            schedule=schedule,
            salary_from=salary_from,
            salary_to=salary_to,
            page=page,
            per_page=per_page,
            **kwargs
        )
        
        vacancies = []
        for item in data.get("items", []):
            try:
                vacancy = self.parse_vacancy(item)
                vacancies.append(vacancy)
            except Exception as e:
                logger.warning(f"⚠️ Ошибка парсинга вакансии: {e}")
                continue
        
        return vacancies
    
    async def get_cities(self, search_text: str = "") -> List[Dict]:
        """Получить список городов для автозаполнения"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/suggests/areas",
                    params={"text": search_text} if search_text else {},
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"❌ Ошибка получения городов: {e}")
            return []


# Глобальный экземпляр сервиса
hh_service = HHService()
