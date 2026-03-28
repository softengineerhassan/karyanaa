from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.schemas.item_schema import (
    RiderItemCreateRequest,
    RiderItemResponse,
    RiderItemUpdateRequest,
)
from app.core.response import success_response
from app.models.user import User
from app.models.rider_item import RiderItem


class ItemActions:
    @staticmethod
    def _to_response(item: RiderItem) -> RiderItemResponse:
        return RiderItemResponse(
            id=item.id,
            user_id=item.user_id,
            rider_id=item.rider_id,
            invoice_number=item.invoice_number,
            item_name=item.item_name,
            quantity=float(item.quantity),
            price=float(item.price),
            weight=float(item.weight),
            discount=float(item.discount),
            subtotal=float(item.subtotal),
            total=float(item.total),
            date=item.purchase_date,
            time=item.purchase_time,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

    @staticmethod
    def create_item(payload: RiderItemCreateRequest, current_user: User, session: Session):
        from app.services.rider_item_service import RiderItemService

        service = RiderItemService(session)
        try:
            item = service.create_item_for_user(current_user.id, payload)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

        return success_response(
            data=ItemActions._to_response(item),
            message="Item created successfully",
            status_code=status.HTTP_201_CREATED,
        )

    @staticmethod
    def list_items(current_user: User, session: Session, rider_id: Optional[UUID] = None):
        from app.services.rider_item_service import RiderItemService

        service = RiderItemService(session)
        try:
            items = service.list_items_for_user(current_user.id, rider_id=rider_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

        data: List[RiderItemResponse] = [ItemActions._to_response(item) for item in items]
        return success_response(data=data, message="Items fetched successfully")

    @staticmethod
    def get_item(item_id: UUID, current_user: User, session: Session):
        from app.services.rider_item_service import RiderItemService

        service = RiderItemService(session)
        item = service.get_item_for_user(item_id, current_user.id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

        return success_response(data=ItemActions._to_response(item), message="Item fetched successfully")

    @staticmethod
    def update_item(item_id: UUID, payload: RiderItemUpdateRequest, current_user: User, session: Session):
        from app.services.rider_item_service import RiderItemService

        service = RiderItemService(session)
        try:
            item = service.update_item_for_user(item_id, current_user.id, payload)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

        return success_response(data=ItemActions._to_response(item), message="Item updated successfully")

    @staticmethod
    def delete_item(item_id: UUID, current_user: User, session: Session):
        from app.services.rider_item_service import RiderItemService

        service = RiderItemService(session)
        deleted = service.delete_item_for_user(item_id, current_user.id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

        return success_response(message="Item deleted successfully")
