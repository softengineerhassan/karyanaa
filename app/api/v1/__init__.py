from fastapi import APIRouter

from app.api.v1.routes import (
    auth_router,
    dashboard_router,
    inventory_router,
    rider_purchase_items_router,
    rider_profiles_router,
    sales_router,
    users_router,
)


# Create main v1 router
api_router = APIRouter()

# Include all route modules in priority order
api_router.include_router(auth_router)
api_router.include_router(dashboard_router)
api_router.include_router(inventory_router)
api_router.include_router(rider_purchase_items_router)
api_router.include_router(rider_profiles_router)
api_router.include_router(sales_router)
api_router.include_router(users_router)


__all__ = ["api_router"]
