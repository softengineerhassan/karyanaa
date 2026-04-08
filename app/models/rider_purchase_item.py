import uuid
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import Date, ForeignKey, Index, Numeric, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class RiderPurchaseItem(BaseModel):
    __tablename__ = "rider_purchase_items"

    owner_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    rider_profile_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("rider_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name: Mapped[str] = mapped_column(String(255), nullable=False)
    item_code: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    barcode: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    brand: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    unit_size: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 3), nullable=True)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    cost_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    purchase_date: Mapped[date] = mapped_column(Date, nullable=False)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    batch_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    supplier_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    supplier_contact: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    payment_status: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    __table_args__ = (
        Index(
            "ix_rider_purchase_items_not_deleted",
            "deleted_at",
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    @property
    def total_price(self) -> Decimal:
        return self.total_amount
