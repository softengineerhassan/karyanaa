import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel

class JWKKey(BaseModel):
    __tablename__ = 'jwk_keys'
    kid: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    public_key: Mapped[str] = mapped_column(Text, nullable=False)
    private_key_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    algorithm: Mapped[str] = mapped_column(String(20), default='RS256', nullable=False)
    key_size: Mapped[int] = mapped_column(default=4096, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rotated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deactivated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    __table_args__ = (Index('ix_jwk_keys_active_current', 'active', 'is_current'),)

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    @property
    def is_usable(self) -> bool:
        return self.active and (not self.is_expired)

    def deactivate(self) -> None:
        self.active = False
        self.is_current = False
        self.deactivated_at = datetime.utcnow()

    def mark_as_rotated(self) -> None:
        self.is_current = False
        self.rotated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f'<JWKKey(id={self.id}, kid={self.kid}, active={self.active})>'