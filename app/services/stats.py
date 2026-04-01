import random


class DailyStatsService:
    def get_today_found_counter(self) -> int:
        return random.randint(1100, 1800)
