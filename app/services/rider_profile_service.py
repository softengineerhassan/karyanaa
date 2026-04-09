import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from app.api.v1.schemas.rider_profile_schema import RiderProfileCreateRequest, RiderProfileUpdateRequest
from app.models.rider_profile import RiderProfile
from app.repos.rider_profile_repository import RiderProfileRepository


class RiderProfileService:
    def __init__(self, session: Session):
        self.session = session
        self.rider_repo = RiderProfileRepository(session)

    def create_rider(self, owner_user_id: uuid.UUID, payload: RiderProfileCreateRequest) -> RiderProfile:
        email = str(payload.email) if payload.email else None

        if self.rider_repo.exists_phone_for_owner(owner_user_id, payload.phone_number):
            raise ValueError("A rider with this phone number already exists")

        if email and self.rider_repo.exists_email_for_owner(owner_user_id, email):
            raise ValueError("A rider with this email already exists")

        return self.rider_repo.create(
            {
                "owner_user_id": owner_user_id,
                "full_name": payload.full_name.strip(),
                "phone_number": payload.phone_number.strip(),
                "email": email,
                "profile_image": payload.profile_image,
            }
        )

    def list_riders(self, owner_user_id: uuid.UUID, search: Optional[str] = None) -> List[RiderProfile]:
        return self.rider_repo.list_by_owner(owner_user_id, search=search)

    def get_rider(self, owner_user_id: uuid.UUID, rider_id: uuid.UUID) -> Optional[RiderProfile]:
        return self.rider_repo.get_by_owner_and_id(owner_user_id, rider_id)

    def update_rider(
        self,
        owner_user_id: uuid.UUID,
        rider_id: uuid.UUID,
        payload: RiderProfileUpdateRequest,
    ) -> Optional[RiderProfile]:
        rider = self.rider_repo.get_by_owner_and_id(owner_user_id, rider_id)
        if not rider:
            return None

        data = payload.model_dump(exclude_unset=True)
        if "full_name" in data and data["full_name"] is not None:
            data["full_name"] = data["full_name"].strip()
        if "phone_number" in data and data["phone_number"] is not None:
            data["phone_number"] = data["phone_number"].strip()

        if "email" in data and data["email"] is not None:
            data["email"] = str(data["email"])

        if "phone_number" in data and data["phone_number"]:
            if self.rider_repo.exists_phone_for_owner(owner_user_id, data["phone_number"], excluded_id=rider_id):
                raise ValueError("A rider with this phone number already exists")

        if "email" in data and data["email"]:
            if self.rider_repo.exists_email_for_owner(owner_user_id, data["email"], excluded_id=rider_id):
                raise ValueError("A rider with this email already exists")

        return self.rider_repo.update(rider_id, data)

    def delete_rider(self, owner_user_id: uuid.UUID, rider_id: uuid.UUID) -> bool:
        rider = self.rider_repo.get_by_owner_and_id(owner_user_id, rider_id)
        if not rider:
            return False
        self.rider_repo.soft_delete(rider_id)
        return True
