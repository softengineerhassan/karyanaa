from typing import List

from fastapi import APIRouter, status

from app.api.v1.handlers.item_handler import ItemHandler
from app.api.v1.schemas.common_schema import StandardResponse
from app.api.v1.schemas.item_schema import RiderItemResponse

router = APIRouter(prefix="/items", tags=["Items"])

router.post(
    "",
    response_model=StandardResponse[RiderItemResponse],
    status_code=status.HTTP_201_CREATED,
)(ItemHandler.create_item)

router.get(
    "",
    response_model=StandardResponse[List[RiderItemResponse]],
    status_code=status.HTTP_200_OK,
)(ItemHandler.list_items)

router.get(
    "/{item_id}",
    response_model=StandardResponse[RiderItemResponse],
    status_code=status.HTTP_200_OK,
)(ItemHandler.get_item)

router.put(
    "/{item_id}",
    response_model=StandardResponse[RiderItemResponse],
    status_code=status.HTTP_200_OK,
)(ItemHandler.update_item)

router.delete(
    "/{item_id}",
    response_model=StandardResponse[None],
    status_code=status.HTTP_200_OK,
)(ItemHandler.delete_item)
