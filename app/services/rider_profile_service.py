from uuid import UUID
from typing import List, Optional

from sqlalchemy.orm import Session

from app.api.v1.schemas.rider_schema import RiderProfileCreateRequest, RiderProfileUpdateRequest
from app.models.rider_profile import RiderProfile
from app.repos.rider_profile_repository import RiderProfileRepository


class RiderProfileService:
    def __init__(self, session: Session):
        self.session = session
        self.rider_profile_repo = RiderProfileRepository(session)

    def create_profile_for_user(
        self,
        user_id: UUID,
        payload: RiderProfileCreateRequest,
    ) -> RiderProfile:
        return self.rider_profile_repo.create(
            {
                "user_id": user_id,
                "name": payload.name,
                "email": payload.email,
                "company_name": payload.company_name,
                "phone_number": payload.phone_number,
            }
        )

    def list_profiles_for_user(self, user_id: UUID) -> List[RiderProfile]:
        return self.rider_profile_repo.list_by_user_id(user_id)

    def get_profile_for_user(self, rider_id: UUID, user_id: UUID) -> Optional[RiderProfile]:
        return self.rider_profile_repo.get_by_id_for_user(rider_id, user_id)

    def update_profile_for_user(
        self,
        rider_id: UUID,
        user_id: UUID,
        payload: RiderProfileUpdateRequest,
    ) -> Optional[RiderProfile]:
        rider_profile = self.rider_profile_repo.get_by_id_for_user(rider_id, user_id)
        if not rider_profile:
            return None

        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            return rider_profile

        for key, value in update_data.items():
            setattr(rider_profile, key, value)

        self.session.flush()
        self.session.refresh(rider_profile)
        return rider_profile

    def delete_profile_for_user(self, rider_id: UUID, user_id: UUID) -> bool:
        rider_profile = self.rider_profile_repo.get_by_id_for_user(rider_id, user_id)
        if not rider_profile:
            return False

        self.rider_profile_repo.soft_delete(rider_profile.id)
        return True
