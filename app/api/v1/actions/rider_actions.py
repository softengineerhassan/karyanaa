from typing import List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.schemas.rider_schema import (
    RiderProfileCreateRequest,
    RiderProfileUpdateRequest,
    RiderProfileResponse,
)
from app.core.response import success_response
from app.models.user import User


class RiderActions:
    @staticmethod
    def create_profile(
        payload: RiderProfileCreateRequest,
        current_user: User,
        session: Session,
    ):
        from app.services.rider_profile_service import RiderProfileService

        service = RiderProfileService(session)
        rider_profile = service.create_profile_for_user(current_user.id, payload)

        return success_response(
            data=RiderProfileResponse.model_validate(rider_profile),
            message="Rider profile created successfully",
            status_code=status.HTTP_201_CREATED,
        )

    @staticmethod
    def list_profiles(current_user: User, session: Session):
        from app.services.rider_profile_service import RiderProfileService

        service = RiderProfileService(session)
        rider_profiles = service.list_profiles_for_user(current_user.id)
        data: List[RiderProfileResponse] = [
            RiderProfileResponse.model_validate(profile)
            for profile in rider_profiles
        ]
        return success_response(data=data, message="Rider profiles fetched successfully")

    @staticmethod
    def get_profile(rider_id: UUID, current_user: User, session: Session):
        from app.services.rider_profile_service import RiderProfileService

        service = RiderProfileService(session)
        rider_profile = service.get_profile_for_user(rider_id, current_user.id)
        if not rider_profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rider profile not found")

        return success_response(
            data=RiderProfileResponse.model_validate(rider_profile),
            message="Rider profile fetched successfully",
        )

    @staticmethod
    def update_profile(
        rider_id: UUID,
        payload: RiderProfileUpdateRequest,
        current_user: User,
        session: Session,
    ):
        from app.services.rider_profile_service import RiderProfileService

        service = RiderProfileService(session)
        rider_profile = service.update_profile_for_user(rider_id, current_user.id, payload)
        if not rider_profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rider profile not found")

        return success_response(
            data=RiderProfileResponse.model_validate(rider_profile),
            message="Rider profile updated successfully",
        )

    @staticmethod
    def delete_profile(rider_id: UUID, current_user: User, session: Session):
        from app.services.rider_profile_service import RiderProfileService

        service = RiderProfileService(session)
        deleted = service.delete_profile_for_user(rider_id, current_user.id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rider profile not found")

        return success_response(message="Rider profile deleted successfully")
