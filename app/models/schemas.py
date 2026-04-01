from dataclasses import dataclass, asdict
from typing import Any


@dataclass(slots=True)
class SearchFilters:
    city_name: str = "Москва"
    city_area_id: str = "1"
    text: str = ""
    age_from: str = ""
    employment: str = ""
    schedule: str = ""
    experience: str = ""
    salary_from: str = ""
    salary_to: str = ""
    page: int = 0

    def to_hh_params(self) -> dict[str, Any]:
        params: dict[str, Any] = {
            "area": self.city_area_id,
            "text": self.text,
            "per_page": 3,
            "page": self.page,
            "order_by": "relevance",
        }
        if self.age_from:
            params["label"] = [self.age_from]
        if self.employment:
            params["employment"] = self.employment
        if self.schedule:
            params["schedule"] = self.schedule
        if self.experience:
            params["experience"] = self.experience
        if self.salary_from:
            params["salary"] = self.salary_from
        if self.salary_to:
            params["salary_to"] = self.salary_to
        return params

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "SearchFilters":
        return cls(**(data or {}))
