from fastapi import APIRouter

from app.api.v1.routes import (
    auth_router,
    inventory_router,
    sales_router,
)


# Create main v1 router
api_router = APIRouter()

# Include all route modules in priority order
api_router.include_router(auth_router)
api_router.include_router(inventory_router)
api_router.include_router(sales_router)


__all__ = ["api_router"]
