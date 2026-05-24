from .auth import router as auth_router
from .products import router as products_router
from .customers import router as customers_router
from .sales import router as sales_router
from .exchange_rate import router as exchange_rate_router

__all__ = [
    "auth_router",
    "products_router",
    "customers_router",
    "sales_router",
    "exchange_rate_router"
]
