from typing import List
from uuid import UUID

from fastapi import APIRouter, status

from app.api.v1.handlers.rider_handler import RiderHandler
from app.api.v1.schemas.common_schema import StandardResponse
from app.api.v1.schemas.rider_schema import RiderProfileResponse

router = APIRouter(prefix="/riders", tags=["Riders"])

router.post(
    "",
    response_model=StandardResponse[RiderProfileResponse],
    status_code=status.HTTP_201_CREATED,
)(RiderHandler.create_profile)

router.post(
    "/profile",
    response_model=StandardResponse[RiderProfileResponse],
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)(RiderHandler.create_profile)

router.get(
    "",
    response_model=StandardResponse[List[RiderProfileResponse]],
    status_code=status.HTTP_200_OK,
)(RiderHandler.list_profiles)

router.get(
    "/{rider_id}",
    response_model=StandardResponse[RiderProfileResponse],
    status_code=status.HTTP_200_OK,
)(RiderHandler.get_profile)

router.put(
    "/{rider_id}",
    response_model=StandardResponse[RiderProfileResponse],
    status_code=status.HTTP_200_OK,
)(RiderHandler.update_profile)

router.delete(
    "/{rider_id}",
    response_model=StandardResponse[None],
    status_code=status.HTTP_200_OK,
)(RiderHandler.delete_profile)
