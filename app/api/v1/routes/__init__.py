from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.inventory import router as inventory_router
from app.api.v1.routes.sales import router as sales_router

__all__ = [
    "auth_router",
    "inventory_router",
    "sales_router",
]
