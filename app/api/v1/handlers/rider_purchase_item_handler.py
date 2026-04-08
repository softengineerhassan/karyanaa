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
        rider_profile_id: Optional[UUID] = Query(None),
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return RiderPurchaseItemActions.list_items(session, current_user, rider_profile_id=rider_profile_id)

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
