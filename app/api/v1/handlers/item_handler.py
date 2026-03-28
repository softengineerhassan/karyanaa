from typing import Optional
from uuid import UUID

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.actions.item_actions import ItemActions
from app.api.v1.schemas.item_schema import RiderItemCreateRequest, RiderItemUpdateRequest
from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User


class ItemHandler:
    @staticmethod
    def create_item(
        payload: RiderItemCreateRequest,
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return ItemActions.create_item(payload, current_user, session)

    @staticmethod
    def list_items(
        rider_id: Optional[UUID] = Query(None),
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return ItemActions.list_items(current_user, session, rider_id=rider_id)

    @staticmethod
    def get_item(
        item_id: UUID,
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return ItemActions.get_item(item_id, current_user, session)

    @staticmethod
    def update_item(
        item_id: UUID,
        payload: RiderItemUpdateRequest,
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return ItemActions.update_item(item_id, payload, current_user, session)

    @staticmethod
    def delete_item(
        item_id: UUID,
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return ItemActions.delete_item(item_id, current_user, session)
