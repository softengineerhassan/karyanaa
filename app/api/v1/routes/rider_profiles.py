from typing import List

from fastapi import APIRouter, status

from app.api.v1.handlers.rider_profile_handler import RiderProfileHandler
from app.api.v1.schemas.common_schema import StandardResponse
from app.api.v1.schemas.rider_profile_schema import RiderProfileResponse


router = APIRouter(prefix="/riders", tags=["Riders"])

router.post("", response_model=StandardResponse[RiderProfileResponse], status_code=status.HTTP_201_CREATED)(RiderProfileHandler.create_rider)
router.get("", response_model=StandardResponse[List[RiderProfileResponse]], status_code=status.HTTP_200_OK)(RiderProfileHandler.list_riders)
router.get("/{rider_id}", response_model=StandardResponse[RiderProfileResponse], status_code=status.HTTP_200_OK)(RiderProfileHandler.get_rider)
router.put("/{rider_id}", response_model=StandardResponse[RiderProfileResponse], status_code=status.HTTP_200_OK)(RiderProfileHandler.update_rider)
router.delete("/{rider_id}", response_model=StandardResponse[None], status_code=status.HTTP_200_OK)(RiderProfileHandler.delete_rider)
