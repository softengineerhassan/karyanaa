from datetime import date, time
from uuid import UUID

from sqlalchemy import Date, ForeignKey, Numeric, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class RiderItem(BaseModel):
    __tablename__ = "rider_items"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rider_id: Mapped[UUID] = mapped_column(
        ForeignKey("rider_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    invoice_number: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    item_name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    weight: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    discount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    subtotal: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    total: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    purchase_date: Mapped[date] = mapped_column(Date, nullable=False)
    purchase_time: Mapped[time] = mapped_column(Time, nullable=False)
