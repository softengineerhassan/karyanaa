import uuid
from typing import List, Optional

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.rider_profile import RiderProfile
from app.repos.base import GenericRepository


class RiderProfileRepository(GenericRepository[RiderProfile]):
    def __init__(self, session: Session):
        super().__init__(RiderProfile, session)

    def get_by_owner_and_id(self, owner_user_id: uuid.UUID, rider_id: uuid.UUID) -> Optional[RiderProfile]:
        query = select(RiderProfile).where(
            RiderProfile.id == rider_id,
            RiderProfile.owner_user_id == owner_user_id,
            RiderProfile.deleted_at.is_(None),
        )
        return self.session.execute(query).scalar_one_or_none()

    def list_by_owner(self, owner_user_id: uuid.UUID, search: Optional[str] = None) -> List[RiderProfile]:
        query = (
            select(RiderProfile)
            .where(
                RiderProfile.owner_user_id == owner_user_id,
                RiderProfile.deleted_at.is_(None),
            )
            .order_by(RiderProfile.created_at.desc())
        )

        if search:
            search_term = f"%{search.strip()}%"
            query = query.where(
                or_(
                    RiderProfile.full_name.ilike(search_term),
                    RiderProfile.phone_number.ilike(search_term),
                    RiderProfile.email.ilike(search_term),
                )
            )

        return list(self.session.execute(query).scalars().all())

    def exists_phone_for_owner(self, owner_user_id: uuid.UUID, phone_number: str, excluded_id: Optional[uuid.UUID] = None) -> bool:
        query = select(RiderProfile.id).where(
            RiderProfile.owner_user_id == owner_user_id,
            RiderProfile.phone_number == phone_number,
            RiderProfile.deleted_at.is_(None),
        )
        if excluded_id:
            query = query.where(RiderProfile.id != excluded_id)
        return self.session.execute(query).scalar_one_or_none() is not None

    def exists_email_for_owner(self, owner_user_id: uuid.UUID, email: str, excluded_id: Optional[uuid.UUID] = None) -> bool:
        query = select(RiderProfile.id).where(
            RiderProfile.owner_user_id == owner_user_id,
            RiderProfile.email == email,
            RiderProfile.deleted_at.is_(None),
        )
        if excluded_id:
            query = query.where(RiderProfile.id != excluded_id)
        return self.session.execute(query).scalar_one_or_none() is not None
