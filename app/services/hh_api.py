import difflib
import re
import time
from typing import Any

import aiohttp
from loguru import logger


class HHClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=8),
            headers={"User-Agent": "HH-Fast-Bot/1.0"},
        )
        self._ru_areas_cache: list[dict[str, str]] | None = None

    async def search_vacancies(self, params: dict[str, Any]) -> dict[str, Any]:
        start = time.perf_counter()
        async with self.session.get(f"{self.base_url}/vacancies", params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()
            duration = time.perf_counter() - start
            if duration > 1.5:  # Логируем если API HH.ru отвечает дольше 1.5 сек
                logger.warning(f"⏱️ HH.ru API тормозит ({duration:.3f}s): {params.get('text', 'no-text')}")
            return data

    async def get_ru_areas(self) -> list[dict[str, str]]:
        if self._ru_areas_cache is not None:
            return self._ru_areas_cache

        async with self.session.get(f"{self.base_url}/areas") as resp:
            resp.raise_for_status()
            data = await resp.json()

        russia = next((country for country in data if str(country.get("id")) == "113"), None)
        if not russia:
            self._ru_areas_cache = []
            return self._ru_areas_cache

        result: list[dict[str, str]] = []

        def walk(nodes: list[dict[str, Any]], parents: list[str]) -> None:
            for node in nodes:
                node_id = str(node.get("id", ""))
                name = str(node.get("name", "")).strip()
                sub_areas = node.get("areas", [])
                if node_id and name:
                    path = parents + [name]
                    # Добавляем как крупные регионы, так и все вложенные населенные пункты.
                    # display_name помогает отличить одинаковые названия в разных регионах.
                    if len(path) > 1:
                        display_name = f"{name} ({', '.join(path[-3:-1])})"
                    else:
                        display_name = name
                    result.append({"id": node_id, "name": name, "display_name": display_name})
                if sub_areas:
                    walk(sub_areas, parents + [name])

        walk(russia.get("areas", []), [])
        uniq_by_id: dict[str, dict[str, str]] = {}
        for item in result:
            uniq_by_id[item["id"]] = item
        self._ru_areas_cache = list(uniq_by_id.values())
        return self._ru_areas_cache

    async def search_ru_areas(self, query: str, limit: int = 15) -> list[dict[str, str]]:
        q = query.strip().lower()
        if not q:
            return []
        areas = await self.get_ru_areas()
        normalized_query = self._normalize_area_name(q)

        exact = [
            a
            for a in areas
            if self._normalize_area_name(a["name"]) == normalized_query
            or self._normalize_area_name(a.get("display_name", "")) == normalized_query
        ]
        starts = [
            a
            for a in areas
            if (
                self._normalize_area_name(a["name"]).startswith(normalized_query)
                or self._normalize_area_name(a.get("display_name", "")).startswith(normalized_query)
            )
            and a not in exact
        ]
        contains = [
            a
            for a in areas
            if (
                normalized_query in self._normalize_area_name(a["name"])
                or normalized_query in self._normalize_area_name(a.get("display_name", ""))
            )
            and a not in exact
            and a not in starts
        ]

        if len(exact) + len(starts) + len(contains) >= limit:
            return (exact + starts + contains)[:limit]

        # Fuzzy fallback for typos (e.g. "Моска", "Екатеринбуг")
        names_map = {}
        for a in areas:
            names_map[self._normalize_area_name(a["name"])] = a
            names_map[self._normalize_area_name(a.get("display_name", ""))] = a
        candidates = difflib.get_close_matches(
            normalized_query,
            list(names_map.keys()),
            n=limit * 3,
            cutoff=0.60,
        )
        fuzzy = []
        for key in candidates:
            area = names_map[key]
            if area not in exact and area not in starts and area not in contains and area not in fuzzy:
                fuzzy.append(area)
        return (exact + starts + contains + fuzzy)[:limit]

    @staticmethod
    def _normalize_area_name(name: str) -> str:
        value = name.lower().replace("ё", "е")
        value = re.sub(r"[^a-zа-я0-9]+", " ", value, flags=re.IGNORECASE)
        return " ".join(value.split())

    async def close(self) -> None:
        await self.session.close()
