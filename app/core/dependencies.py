
from typing import Optional, List
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core import security
from app.models.user import User
from app.repos.user_repository import UserRepository
from app.utils.exceptions import (
    InvalidTokenError,
    ExpiredTokenError,
    MissingTokenError,
    UserNotFoundError,
    UserInactiveError,
    PermissionDeniedError,
    RevokedTokenError,
)

# Redis disabled - uncomment to enable caching
# from app.cache.redis_client import RedisClient, get_redis_client


# ============================================
# Security Scheme
# ============================================

security_scheme = HTTPBearer(
    scheme_name="Bearer",
    description="JWT Bearer token authentication"
)


# ============================================
# Token Validation
# ============================================

def get_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> dict:
    if not credentials:
        raise MissingTokenError()
    
    token = credentials.credentials
    
    try:
        # Decode and verify token
        payload = security.verify_token(token, token_type="access")
        
        # Redis disabled - uncomment to enable token blacklist check
        # jti = payload.get("jti")
        # if jti:
        #     is_blacklisted = redis.is_token_blacklisted(jti)
        #     if is_blacklisted:
        #         raise RevokedTokenError()
        
        return payload
        
    except ExpiredTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except RevokedTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ============================================
# Current User Dependencies
# ============================================

def get_current_user(
    payload: dict = Depends(get_token_payload),
    session: Session = Depends(get_db)
) -> User:
    try:
        user_id = UUID(payload["sub"])
    except (KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_repo = UserRepository(session)
    user = user_repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    # Reject staff tokens from user-based APIs
    if payload.get("type") == "staff":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type for this operation",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    return current_user


def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser privileges required",
        )
    
    return current_user


def get_current_verified_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required",
        )
    
    return current_user


# ============================================
# Staff Dependencies (PIN-based)
# ============================================

def get_current_staff(
    payload: dict = Depends(get_token_payload),
    session: Session = Depends(get_db)
) -> dict:
    if payload.get("type") != "staff":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Valid staff token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    venue_id_str = payload.get("venue_id")
    if not venue_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing venue context",
        )
    
    try:
        venue_id = UUID(venue_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid venue ID in token",
        )
    
    # Verify venue exists
    from app.repos.venue_repository import VenueRepository
    venue_repo = VenueRepository(session)
    venue = venue_repo.get_by_id(venue_id)
    
    if not venue:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Venue no longer exists or is inactive",
        )
    
    return {
        "venue_id": venue_id,
        "scopes": payload.get("scopes", []),
        "type": "staff"
    }


# ============================================
# Optional Current User (for mixed auth endpoints)
# ============================================

def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    session: Session = Depends(get_db),
) -> Optional[User]:
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = security.verify_token(token, token_type="access")
        
        # Redis disabled - token blacklist check skipped
        
        user_id = UUID(payload["sub"])
        user_repo = UserRepository(session)
        user = user_repo.get_by_id(user_id)
        
        if user and user.is_active:
            return user
        
        return None
        
    except Exception:
        return None


# ============================================
# Service Dependencies
# ============================================

def get_auth_service(
    session: Session = Depends(get_db),
):
    from app.services.auth_service import AuthService
    return AuthService(session)


def get_user_service(
    session: Session = Depends(get_db),
) -> object:
    from app.services.user_service import UserService
    return UserService(session)


def get_permission_service(
    session: Session = Depends(get_db),
):
    from app.services.permission_service import PermissionService
    return PermissionService(session)


# ============================================
# Permission Validation
# ============================================

class PermissionChecker:
    
    def __init__(self, required_permissions: List[str], require_all: bool = True):
        self.required_permissions = required_permissions
        self.require_all = require_all
    
    def __call__(
        self,
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_db),
    ) -> User:
        # Superusers bypass all permission checks
        if current_user.is_superuser:
            return current_user
        
        # Get permission service
        from app.services.permission_service import PermissionService
        perm_service = PermissionService(session)
        
        # Check permissions
        has_permission = perm_service.check_permissions(
            user_id=current_user.id,
            permission_names=self.required_permissions,
            require_all=self.require_all,
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permissions: {', '.join(self.required_permissions)}"
            )
        
        return current_user


class RoleChecker:
    
    def __init__(self, required_roles: List[str], require_all: bool = False):
        self.required_roles = required_roles
        self.require_all = require_all
    
    def __call__(
        self,
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_db)
    ) -> User:
        # Superusers bypass all role checks
        if current_user.is_superuser:
            return current_user
        
        # Get role repository
        from app.repos.role_repository import RoleRepository
        role_repo = RoleRepository(session)
        
        # Get user roles
        user_roles = role_repo.get_user_roles(current_user.id)
        user_role_names = {role.name for role in user_roles}
        required_role_set = set(self.required_roles)
        
        # Check roles
        if self.require_all:
            has_roles = required_role_set.issubset(user_role_names)
        else:
            has_roles = bool(required_role_set.intersection(user_role_names))
        
        if not has_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required roles: {', '.join(self.required_roles)}"
            )
        
        return current_user



# ============================================
# Pagination Dependencies
# ============================================

def get_pagination_params(
    page: int = 1,
    page_size: int = 20
) -> dict:
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 1
    if page_size > 100:
        page_size = 100
    
    offset = (page - 1) * page_size
    
    return {
        "page": page,
        "page_size": page_size,
        "offset": offset,
        "limit": page_size
    }
