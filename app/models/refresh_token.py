import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel
if TYPE_CHECKING:
    from app.models.user import User

class RefreshToken(BaseModel):
    __tablename__ = 'refresh_tokens'
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True, comment="SHA256 hash of the refresh token")
    jti: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    device_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    device_info: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_reason: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    user: Mapped['User'] = relationship('User', back_populates='refresh_tokens')
    __table_args__ = (Index('ix_refresh_tokens_user_revoked', 'user_id', 'revoked'), Index('ix_refresh_tokens_expires_revoked', 'expires_at', 'revoked'))

    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at

    @property
    def is_valid(self) -> bool:
        return not self.is_expired and (not self.revoked)

    def revoke(self, reason: str='manual_revoke') -> None:
        self.revoked = True
        self.revoked_at = datetime.utcnow()
        self.revoked_reason = reason

    def update_last_used(self) -> None:
        self.last_used_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f'<RefreshToken(id={self.id}, jti={self.jti}, revoked={self.revoked})>'