from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rider_profile import RiderProfile
from app.repos.base import GenericRepository


class RiderProfileRepository(GenericRepository[RiderProfile]):
    def __init__(self, session: Session):
        super().__init__(RiderProfile, session)

    def list_by_user_id(self, user_id: UUID) -> List[RiderProfile]:
        query = select(RiderProfile).where(
            RiderProfile.user_id == user_id,
            RiderProfile.deleted_at.is_(None),
        ).order_by(RiderProfile.created_at.desc())
        result = self.session.execute(query)
        return list(result.scalars().all())

    def get_by_id_for_user(self, rider_id: UUID, user_id: UUID) -> Optional[RiderProfile]:
        query = select(RiderProfile).where(
            RiderProfile.id == rider_id,
            RiderProfile.user_id == user_id,
            RiderProfile.deleted_at.is_(None),
        )
        result = self.session.execute(query)
        return result.scalar_one_or_none()
