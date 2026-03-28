from typing import List

from fastapi import APIRouter, status

from app.api.v1.handlers.inventory_handler import InventoryHandler
from app.api.v1.schemas.common_schema import StandardResponse
from app.api.v1.schemas.inventory_schema import (
    CategoryResponse,
    ProductResponse,
    UnitResponse,
)

router = APIRouter(prefix="/inventory", tags=["Inventory"])

router.post("/categories", response_model=StandardResponse[CategoryResponse], status_code=status.HTTP_201_CREATED)(InventoryHandler.create_category)
router.get("/categories", response_model=StandardResponse[List[CategoryResponse]], status_code=status.HTTP_200_OK)(InventoryHandler.list_categories)
router.get("/categories/{category_id}", response_model=StandardResponse[CategoryResponse], status_code=status.HTTP_200_OK)(InventoryHandler.get_category)
router.put("/categories/{category_id}", response_model=StandardResponse[CategoryResponse], status_code=status.HTTP_200_OK)(InventoryHandler.update_category)
router.delete("/categories/{category_id}", response_model=StandardResponse[None], status_code=status.HTTP_200_OK)(InventoryHandler.delete_category)

router.post("/units", response_model=StandardResponse[UnitResponse], status_code=status.HTTP_201_CREATED)(InventoryHandler.create_unit)
router.get("/units", response_model=StandardResponse[List[UnitResponse]], status_code=status.HTTP_200_OK)(InventoryHandler.list_units)
router.get("/units/{unit_id}", response_model=StandardResponse[UnitResponse], status_code=status.HTTP_200_OK)(InventoryHandler.get_unit)
router.put("/units/{unit_id}", response_model=StandardResponse[UnitResponse], status_code=status.HTTP_200_OK)(InventoryHandler.update_unit)
router.delete("/units/{unit_id}", response_model=StandardResponse[None], status_code=status.HTTP_200_OK)(InventoryHandler.delete_unit)

router.post("/products", response_model=StandardResponse[ProductResponse], status_code=status.HTTP_201_CREATED)(InventoryHandler.create_product)
router.get("/products", response_model=StandardResponse[List[ProductResponse]], status_code=status.HTTP_200_OK)(InventoryHandler.list_products)
router.get("/products/{product_id}", response_model=StandardResponse[ProductResponse], status_code=status.HTTP_200_OK)(InventoryHandler.get_product)
router.put("/products/{product_id}", response_model=StandardResponse[ProductResponse], status_code=status.HTTP_200_OK)(InventoryHandler.update_product)
router.delete("/products/{product_id}", response_model=StandardResponse[None], status_code=status.HTTP_200_OK)(InventoryHandler.delete_product)
