from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.inventory import router as inventory_router
from app.api.v1.routes.rider_purchase_items import router as rider_purchase_items_router
from app.api.v1.routes.rider_profiles import router as rider_profiles_router
from app.api.v1.routes.sales import router as sales_router
from app.api.v1.routes.users import router as users_router

__all__ = [
    "auth_router",
    "inventory_router",
    "rider_purchase_items_router",
    "rider_profiles_router",
    "sales_router",
    "users_router",
]
