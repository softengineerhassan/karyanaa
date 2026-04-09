from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.actions.rider_purchase_item_actions import RiderPurchaseItemActions
from app.api.v1.schemas.rider_purchase_item_schema import RiderPurchaseItemCreateRequest, RiderPurchaseItemUpdateRequest
from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User


class RiderPurchaseItemHandler:
    @staticmethod
    def create_item(
        payload: RiderPurchaseItemCreateRequest,
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return RiderPurchaseItemActions.create_item(payload, session, current_user)

    @staticmethod
    def list_items(
        search: Optional[str] = Query(None, description="Search by rider name or item name"),
        rider_profile_id: Optional[UUID] = Query(None),
        start_date: Optional[date] = Query(None, description="Filter by purchase date from"),
        end_date: Optional[date] = Query(None, description="Filter by purchase date to"),
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return RiderPurchaseItemActions.list_items(
            session,
            current_user,
            search=search,
            rider_profile_id=rider_profile_id,
            start_date=start_date,
            end_date=end_date,
        )

    @staticmethod
    def get_item(
        item_id: UUID,
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return RiderPurchaseItemActions.get_item(item_id, session, current_user)

    @staticmethod
    def update_item(
        item_id: UUID,
        payload: RiderPurchaseItemUpdateRequest,
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return RiderPurchaseItemActions.update_item(item_id, payload, session, current_user)

    @staticmethod
    def delete_item(
        item_id: UUID,
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return RiderPurchaseItemActions.delete_item(item_id, session, current_user)
