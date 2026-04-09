from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.schemas.rider_profile_schema import (
    RiderProfileCreateRequest,
    RiderProfileResponse,
    RiderProfileUpdateRequest,
)
from app.core.response import success_response
from app.models.user import User
from app.services.rider_profile_service import RiderProfileService


class RiderProfileActions:
    @staticmethod
    def create_rider(payload: RiderProfileCreateRequest, session: Session, current_user: User):
        service = RiderProfileService(session)
        try:
            rider = service.create_rider(current_user.id, payload)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
        return success_response(data=RiderProfileResponse.model_validate(rider), message="Rider profile created successfully")

    @staticmethod
    def list_riders(search: str | None, session: Session, current_user: User):
        service = RiderProfileService(session)
        riders = service.list_riders(current_user.id, search=search)
        data = [RiderProfileResponse.model_validate(item) for item in riders]
        return success_response(data=data, message="Rider profiles fetched successfully")

    @staticmethod
    def get_rider(rider_id: UUID, session: Session, current_user: User):
        service = RiderProfileService(session)
        rider = service.get_rider(current_user.id, rider_id)
        if not rider:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rider profile not found")
        return success_response(data=RiderProfileResponse.model_validate(rider), message="Rider profile fetched successfully")

    @staticmethod
    def update_rider(rider_id: UUID, payload: RiderProfileUpdateRequest, session: Session, current_user: User):
        service = RiderProfileService(session)
        try:
            rider = service.update_rider(current_user.id, rider_id, payload)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

        if not rider:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rider profile not found")

        return success_response(data=RiderProfileResponse.model_validate(rider), message="Rider profile updated successfully")

    @staticmethod
    def delete_rider(rider_id: UUID, session: Session, current_user: User):
        service = RiderProfileService(session)
        if not service.delete_rider(current_user.id, rider_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rider profile not found")
        return success_response(message="Rider profile deleted successfully")
