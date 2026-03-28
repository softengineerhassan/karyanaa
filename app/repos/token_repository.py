from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.core import security
from app.models.refresh_token import RefreshToken
from app.repos.base import GenericRepository


class TokenRepository(GenericRepository[RefreshToken]):
    def __init__(self, session: Session):
        super().__init__(RefreshToken, session)

    def find_by_token(self, token: str) -> RefreshToken | None:
        token_hash = security.hash_token(token)
        stmt = select(RefreshToken).where(
            and_(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked.is_(False),
                RefreshToken.deleted_at.is_(None),
            )
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def revoke_user_tokens(self, user_id: UUID) -> int:
        stmt = select(RefreshToken).where(
            and_(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked.is_(False),
                RefreshToken.deleted_at.is_(None),
            )
        )
        tokens = list(self.session.execute(stmt).scalars().all())
        now = datetime.utcnow()

        for token in tokens:
            token.revoked = True
            token.revoked_at = now
            token.revoked_reason = "revoke_all"

        self.session.flush()
        return len(tokens)
