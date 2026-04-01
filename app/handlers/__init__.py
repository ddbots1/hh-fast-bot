from aiogram import Dispatcher

from .favorites import router as favorites_router
from .filters import router as filters_router
from .menu import router as menu_router
from .search import router as search_router
from .start import router as start_router
from .errors import router as errors_router


def register_routers(dp: Dispatcher) -> None:
    dp.include_router(errors_router)
    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(filters_router)
    dp.include_router(search_router)
    dp.include_router(favorites_router)
