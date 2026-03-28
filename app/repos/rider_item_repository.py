from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rider_item import RiderItem
from app.repos.base import GenericRepository


class RiderItemRepository(GenericRepository[RiderItem]):
    def __init__(self, session: Session):
        super().__init__(RiderItem, session)

    def list_by_user_id(self, user_id: UUID, rider_id: Optional[UUID] = None) -> List[RiderItem]:
        query = select(RiderItem).where(
            RiderItem.user_id == user_id,
            RiderItem.deleted_at.is_(None),
        )
        if rider_id:
            query = query.where(RiderItem.rider_id == rider_id)

        query = query.order_by(RiderItem.purchase_date.desc(), RiderItem.purchase_time.desc())
        result = self.session.execute(query)
        return list(result.scalars().all())

    def get_by_id_for_user(self, item_id: UUID, user_id: UUID) -> Optional[RiderItem]:
        query = select(RiderItem).where(
            RiderItem.id == item_id,
            RiderItem.user_id == user_id,
            RiderItem.deleted_at.is_(None),
        )
        result = self.session.execute(query)
        return result.scalar_one_or_none()
