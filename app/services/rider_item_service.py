from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.api.v1.schemas.item_schema import RiderItemCreateRequest, RiderItemUpdateRequest
from app.models.rider_item import RiderItem
from app.repos.rider_item_repository import RiderItemRepository
from app.repos.rider_profile_repository import RiderProfileRepository


class RiderItemService:
    def __init__(self, session: Session):
        self.session = session
        self.item_repo = RiderItemRepository(session)
        self.rider_repo = RiderProfileRepository(session)

    @staticmethod
    def _to_amount(value: float) -> Decimal:
        return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def _generate_invoice_number() -> str:
        stamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"INV-{stamp}-{uuid4().hex[:8].upper()}"

    def _calculate_totals(self, quantity: Decimal, price: Decimal, weight: Decimal, discount: Decimal) -> tuple[Decimal, Decimal]:
        # POS-style line formula:
        # gross = quantity * unit_price * weight
        # discount_amount = gross * (discount_percent / 100)
        # net_total = gross - discount_amount
        subtotal = (quantity * price * weight).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        discount_amount = (subtotal * (discount / Decimal("100"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total = (subtotal - discount_amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if total < Decimal("0.00"):
            total = Decimal("0.00")
        return subtotal, total

    def _ensure_rider_owned_by_user(self, rider_id: UUID, user_id: UUID) -> None:
        rider = self.rider_repo.get_by_id_for_user(rider_id, user_id)
        if not rider:
            raise ValueError("Rider profile not found")

    def create_item_for_user(self, user_id: UUID, payload: RiderItemCreateRequest) -> RiderItem:
        self._ensure_rider_owned_by_user(payload.rider_id, user_id)

        quantity = self._to_amount(payload.quantity)
        price = self._to_amount(payload.price)
        weight = self._to_amount(payload.weight)
        discount = self._to_amount(payload.discount)
        subtotal, total = self._calculate_totals(quantity, price, weight, discount)

        return self.item_repo.create(
            {
                "user_id": user_id,
                "rider_id": payload.rider_id,
                "invoice_number": self._generate_invoice_number(),
                "item_name": payload.item_name,
                "quantity": quantity,
                "price": price,
                "weight": weight,
                "discount": discount,
                "subtotal": subtotal,
                "total": total,
                "purchase_date": payload.date,
                "purchase_time": payload.time,
            }
        )

    def list_items_for_user(self, user_id: UUID, rider_id: Optional[UUID] = None) -> List[RiderItem]:
        if rider_id:
            self._ensure_rider_owned_by_user(rider_id, user_id)
        return self.item_repo.list_by_user_id(user_id, rider_id)

    def get_item_for_user(self, item_id: UUID, user_id: UUID) -> Optional[RiderItem]:
        return self.item_repo.get_by_id_for_user(item_id, user_id)

    def update_item_for_user(self, item_id: UUID, user_id: UUID, payload: RiderItemUpdateRequest) -> Optional[RiderItem]:
        item = self.item_repo.get_by_id_for_user(item_id, user_id)
        if not item:
            return None

        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            return item

        if "rider_id" in update_data and update_data["rider_id"] is not None:
            self._ensure_rider_owned_by_user(update_data["rider_id"], user_id)

        if "item_name" in update_data:
            item.item_name = update_data["item_name"]
        if "rider_id" in update_data and update_data["rider_id"] is not None:
            item.rider_id = update_data["rider_id"]
        if "date" in update_data and update_data["date"] is not None:
            item.purchase_date = update_data["date"]
        if "time" in update_data and update_data["time"] is not None:
            item.purchase_time = update_data["time"]

        quantity = self._to_amount(update_data["quantity"]) if "quantity" in update_data else self._to_amount(float(item.quantity))
        price = self._to_amount(update_data["price"]) if "price" in update_data else self._to_amount(float(item.price))
        weight = self._to_amount(update_data["weight"]) if "weight" in update_data else self._to_amount(float(item.weight))
        discount = self._to_amount(update_data["discount"]) if "discount" in update_data else self._to_amount(float(item.discount))

        item.quantity = quantity
        item.price = price
        item.weight = weight
        item.discount = discount

        subtotal, total = self._calculate_totals(quantity, price, weight, discount)
        item.subtotal = subtotal
        item.total = total

        self.session.flush()
        self.session.refresh(item)
        return item

    def delete_item_for_user(self, item_id: UUID, user_id: UUID) -> bool:
        item = self.item_repo.get_by_id_for_user(item_id, user_id)
        if not item:
            return False

        self.item_repo.soft_delete(item.id)
        return True
