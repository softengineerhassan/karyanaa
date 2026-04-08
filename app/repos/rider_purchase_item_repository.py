import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rider_purchase_item import RiderPurchaseItem
from app.repos.base import GenericRepository


class RiderPurchaseItemRepository(GenericRepository[RiderPurchaseItem]):
    def __init__(self, session: Session):
        super().__init__(RiderPurchaseItem, session)

    def get_by_owner_and_id(self, owner_user_id: uuid.UUID, item_id: uuid.UUID) -> Optional[RiderPurchaseItem]:
        query = select(RiderPurchaseItem).where(
            RiderPurchaseItem.id == item_id,
            RiderPurchaseItem.owner_user_id == owner_user_id,
            RiderPurchaseItem.deleted_at.is_(None),
        )
        return self.session.execute(query).scalar_one_or_none()

    def list_by_owner(
        self,
        owner_user_id: uuid.UUID,
        rider_profile_id: Optional[uuid.UUID] = None,
    ) -> List[RiderPurchaseItem]:
        query = select(RiderPurchaseItem).where(
            RiderPurchaseItem.owner_user_id == owner_user_id,
            RiderPurchaseItem.deleted_at.is_(None),
        )
        if rider_profile_id is not None:
            query = query.where(RiderPurchaseItem.rider_profile_id == rider_profile_id)

        query = query.order_by(RiderPurchaseItem.purchase_date.desc(), RiderPurchaseItem.created_at.desc())
        return list(self.session.execute(query).scalars().all())
