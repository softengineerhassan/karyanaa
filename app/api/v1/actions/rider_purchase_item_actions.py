from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.schemas.rider_purchase_item_schema import (
    RiderPurchaseItemCreateRequest,
    RiderPurchaseItemResponse,
    RiderPurchaseItemUpdateRequest,
)
from app.core.response import success_response
from app.models.user import User
from app.services.rider_purchase_item_service import RiderPurchaseItemService


class RiderPurchaseItemActions:
    @staticmethod
    def create_item(payload: RiderPurchaseItemCreateRequest, session: Session, current_user: User):
        service = RiderPurchaseItemService(session)
        try:
            item = service.create_item(current_user.id, payload)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
        return success_response(data=RiderPurchaseItemResponse.model_validate(item), message="Rider purchase item created successfully")

    @staticmethod
    def list_items(
        session: Session,
        current_user: User,
        search: Optional[str] = None,
        rider_profile_id: Optional[UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ):
        service = RiderPurchaseItemService(session)
        try:
            items = service.list_items(
                current_user.id,
                search=search,
                rider_profile_id=rider_profile_id,
                start_date=start_date,
                end_date=end_date,
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

        data = [RiderPurchaseItemResponse.model_validate(item) for item in items]
        return success_response(data=data, message="Rider purchase items fetched successfully")

    @staticmethod
    def get_item(item_id: UUID, session: Session, current_user: User):
        service = RiderPurchaseItemService(session)
        item = service.get_item(current_user.id, item_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rider purchase item not found")
        return success_response(data=RiderPurchaseItemResponse.model_validate(item), message="Rider purchase item fetched successfully")

    @staticmethod
    def update_item(item_id: UUID, payload: RiderPurchaseItemUpdateRequest, session: Session, current_user: User):
        service = RiderPurchaseItemService(session)
        try:
            item = service.update_item(current_user.id, item_id, payload)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rider purchase item not found")

        return success_response(data=RiderPurchaseItemResponse.model_validate(item), message="Rider purchase item updated successfully")

    @staticmethod
    def delete_item(item_id: UUID, session: Session, current_user: User):
        service = RiderPurchaseItemService(session)
        if not service.delete_item(current_user.id, item_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rider purchase item not found")
        return success_response(message="Rider purchase item deleted successfully")
