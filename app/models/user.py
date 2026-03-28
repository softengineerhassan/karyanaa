import uuid
from datetime import datetime, date
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Boolean, DateTime, Date, Index, Integer, String, Text, func, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.refresh_token import RefreshToken

class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_email_verified = mapped_column(Boolean, default=False, nullable=False)
    email_verified_at = mapped_column(DateTime(timezone=True), nullable=True)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    profile_picture: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_gold: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_vip: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fcm_token: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    joined_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan", lazy="selectin")

    __table_args__ = (
        Index("ix_users_email_active", "email", "is_active"),
        Index(
            "ix_users_not_deleted",
            "deleted_at",
            postgresql_where=text("deleted_at IS NULL")
        ),
    )

    @property
    def is_locked(self) -> bool:
        return self.locked_until is not None and datetime.utcnow() < self.locked_until

    def increment_failed_login(self) -> None:
        self.failed_login_attempts += 1

    def reset_failed_login(self) -> None:
        self.failed_login_attempts = 0
        self.locked_until = None

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
