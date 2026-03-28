from fastapi import APIRouter

from app.api.v1.routes import (
    auth_router,
    riders_router,
    items_router,
)


# Create main v1 router
api_router = APIRouter()

# Include all route modules in priority order
api_router.include_router(auth_router)
api_router.include_router(riders_router)
api_router.include_router(items_router)


__all__ = ["api_router"]
