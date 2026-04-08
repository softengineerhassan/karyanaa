from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from app.api.v1.schemas.auth_schema import CurrentUserResponse, RoleResponse, UserPublicResponse, RecentActivity
from app.models.user import User
from app.core.config import settings

if TYPE_CHECKING:
    from app.api.v1.schemas.user_schema import UserResponse, UserDetailResponse


def build_profile_picture_url(key: Optional[str]) -> Optional[str]:
    if not key:
        return None
    if settings.AWS_CLOUDFRONT_DOMAIN:
        return f"https://{settings.AWS_CLOUDFRONT_DOMAIN}/{key}"
    return (
        f"https://{settings.AWS_S3_BUCKET}.s3."
        f"{settings.AWS_REGION}.amazonaws.com/{key}"
    )


def normalize_public_email(user: User) -> str:
    email = (user.email or "").strip()
    if not email:
        return f"user-{user.id}@employee.karyanaa.app"

    # Keep legacy placeholder domains from breaking EmailStr validation in API responses.
    if email.endswith("@employee.local") or email.endswith("@employee.localhost"):
        return f"user-{user.id}@employee.karyanaa.app"

    return email


def _calculate_loyalty_stats(bookings_count: int) -> dict:
    is_gold = 10 < bookings_count < 20
    is_vip = bookings_count >= 30
    
    remaining_to_gold = None
    remaining_to_vip = None
    
    if bookings_count <= 10:
        remaining_to_gold = 11 - bookings_count
    
    if bookings_count < 30:
        remaining_to_vip = 30 - bookings_count
        
    return {
        "is_gold": is_gold,
        "is_vip": is_vip,
        "bookings_count": bookings_count,
        "remaining_to_gold": remaining_to_gold,
        "remaining_to_vip": remaining_to_vip
    }


def map_user_to_user_response(user: User, bookings_count: int = 0) -> "UserResponse":
    from app.api.v1.schemas.user_schema import UserResponse
    primary_role = user.user_roles[0] if getattr(user, "user_roles", None) else None
    loyalty = _calculate_loyalty_stats(bookings_count)
    
    return UserResponse(
        id=user.id,
        employee_id=user.employee_id,
        email=normalize_public_email(user),
        full_name=user.full_name,
        phone_number=user.phone_number,
        location=user.location,
        bio=user.bio,
        date_of_birth=user.date_of_birth,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        is_email_verified=user.is_email_verified,
        email_verified_at=user.email_verified_at,
        last_login_at=user.last_login_at,
        last_login_ip=user.last_login_ip,
        joined_date = user.joined_date,
        created_at=user.created_at,
        updated_at=user.updated_at,
        role_id=primary_role.role_id if primary_role else None,
        role_name=(primary_role.role.name if primary_role and primary_role.role else None),
        profile_picture_url=build_profile_picture_url(user.profile_picture),
        **loyalty
    )


def map_user_to_user_detail_response(user: User, bookings_count: int = 0) -> "UserDetailResponse":
    from app.api.v1.schemas.user_schema import UserDetailResponse
    loyalty = _calculate_loyalty_stats(bookings_count)
    return UserDetailResponse(
        id=user.id,
        employee_id=user.employee_id,
        email=normalize_public_email(user),
        full_name=user.full_name,
        phone_number=user.phone_number,
        location=user.location,
        bio=user.bio,
        date_of_birth=user.date_of_birth,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        is_email_verified=user.is_email_verified,
        email_verified_at=user.email_verified_at,
        last_login_at=user.last_login_at,
        last_login_ip=user.last_login_ip,
        joined_date = user.joined_date,
        created_at=user.created_at,
        updated_at=user.updated_at,
        failed_login_attempts=user.failed_login_attempts or 0,
        locked_until=user.locked_until,
        roles=[
            {
                "id": ur.role.id,
                "name": ur.role.name,
            }
            for ur in getattr(user, "user_roles", [])
            if ur.role is not None
        ],
        permissions=[], # Placeholder or implement permission mapping if needed
        extra_data=None, # Explicitly safe
        profile_picture_url=build_profile_picture_url(user.profile_picture),
        **loyalty
    )


def map_user_to_public_response(user: User, bookings_count: int = 0, session=None) -> UserPublicResponse:
    return UserPublicResponse(
        id=user.id,
        employee_id=user.employee_id,
        email=normalize_public_email(user),
        full_name=user.full_name,
        phone_number=user.phone_number,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        is_email_verified=user.is_email_verified,
        created_at=user.created_at,
        last_login_at=user.last_login_at,
        roles=[
            RoleResponse(
                id=ur.role.id,
                name=ur.role.name,
            )
            for ur in getattr(user, "user_roles", [])
            if ur.role is not None
        ],
        profile_picture_url=build_profile_picture_url(user.profile_picture),
    )


def map_user_to_current_user_response(user: User, bookings_count: int = 0, session=None) -> CurrentUserResponse:
    actions_taken = 0
    approvals = 0
    revenue_impact = 0.0
    time_active_str = "0h"

    if session is not None:
        # This repository is optional in trimmed deployments; keep profile APIs functional without it.
        try:
            from app.repos.venue_repository import VenueRepository

            # Keep only high-level stats for auth profile response.
            actions_taken = 0

            admin_stats = VenueRepository(session).get_admin_stats(user.id)
            approvals = admin_stats["approvals"]
            revenue_impact = admin_stats["revenue_impact"]
        except Exception:
            approvals = 0
            revenue_impact = 0.0

    # Calculate Time Active
    if user.joined_date or user.created_at:
        start_date = user.joined_date or user.created_at
        if start_date.tzinfo is None:
            from datetime import timezone
            start_date = start_date.replace(tzinfo=timezone.utc)
        
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        diff = now - start_date
        hours = int(diff.total_seconds() // 3600)
        time_active_str = f"{hours}h"

    return CurrentUserResponse(
        id=user.id,
        employee_id=user.employee_id,
        email=normalize_public_email(user),
        full_name=user.full_name,
        phone_number=user.phone_number,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        is_email_verified=user.is_email_verified,
        created_at=user.created_at if user.created_at else datetime.now(),
        last_login_at=user.last_login_at,
        roles=[
            RoleResponse(
                id=ur.role.id,
                name=ur.role.name,
            )
            for ur in getattr(user, "user_roles", [])
            if ur.role is not None
        ],
        profile_picture_url=build_profile_picture_url(user.profile_picture),
        actions_taken=actions_taken,
        time_active=time_active_str,
        approvals=approvals,
        revenue_impact=f"+PKR {revenue_impact:,.1f}" if revenue_impact > 0 else f"PKR {revenue_impact:,.1f}",
    )
