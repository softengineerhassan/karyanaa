from typing import List

from fastapi import APIRouter, status

from app.api.v1.handlers.rider_purchase_item_handler import RiderPurchaseItemHandler
from app.api.v1.schemas.common_schema import StandardResponse
from app.api.v1.schemas.rider_purchase_item_schema import RiderPurchaseItemResponse


router = APIRouter(prefix="/rider-purchase-items", tags=["Rider Purchase Items"])

router.post("", response_model=StandardResponse[RiderPurchaseItemResponse], status_code=status.HTTP_201_CREATED)(RiderPurchaseItemHandler.create_item)
router.get("", response_model=StandardResponse[List[RiderPurchaseItemResponse]], status_code=status.HTTP_200_OK)(RiderPurchaseItemHandler.list_items)
router.get("/{item_id}", response_model=StandardResponse[RiderPurchaseItemResponse], status_code=status.HTTP_200_OK)(RiderPurchaseItemHandler.get_item)
router.put("/{item_id}", response_model=StandardResponse[RiderPurchaseItemResponse], status_code=status.HTTP_200_OK)(RiderPurchaseItemHandler.update_item)
router.delete("/{item_id}", response_model=StandardResponse[None], status_code=status.HTTP_200_OK)(RiderPurchaseItemHandler.delete_item)
