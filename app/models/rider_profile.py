import uuid
from typing import Optional

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class RiderProfile(BaseModel):
    __tablename__ = "rider_profiles"

    owner_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    profile_image: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    __table_args__ = (
        UniqueConstraint("owner_user_id", "phone_number", name="uq_rider_profiles_owner_phone"),
        UniqueConstraint("owner_user_id", "email", name="uq_rider_profiles_owner_email"),
        Index(
            "ix_rider_profiles_not_deleted",
            "deleted_at",
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )
