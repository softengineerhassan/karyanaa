from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User

class UserOTP(BaseModel):
    __tablename__ = "user_otps"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(10), nullable=False)
    purpose: Mapped[str] = mapped_column(String(50), nullable=False, default="email_verification")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return f"<UserOTP(user_id={self.user_id}, code={self.code}, purpose={self.purpose})>"
