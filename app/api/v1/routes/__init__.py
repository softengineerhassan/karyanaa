from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.riders import router as riders_router
from app.api.v1.routes.items import router as items_router

__all__ = [
    "auth_router",
    "riders_router",
    "items_router",
]
