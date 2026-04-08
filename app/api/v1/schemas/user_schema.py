from typing import Optional, Dict, Any, List
from datetime import datetime, date
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr, ConfigDict

from app.api.v1.schemas.common_schema import BaseSchema, PaginationMeta
from app.api.v1.enums.user_enum import UserRoleFilter, UserStatusFilter, UserSegment
from app.api.v1.schemas.auth_schema import RecentActivity


from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from typing import Optional, Dict, Any

class UserCreateRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    full_name: str = Field(..., min_length=2, max_length=255, description="User full name")
    phone_number: Optional[str] = Field(None, max_length=20, description="User phone number")
    is_active: bool = Field(True, description="User active status")
    is_superuser: bool = Field(False, description="Superuser status")
    role_id: UUID = Field(..., description="Role ID of the user (UUID)")  # Changed to UUID
    location: Optional[str] = Field(None, max_length=255, description="User location")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="Additional user data")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "admin@example.com",
                "password": "SecurePass123!",
                "full_name": "Admin User",
                "phone_number": "+1234567890",
                "role_id": "3e5bb683-0dbf-4af7-8ab0-35936c36791e",  # UUID example
                "is_active": True,
                "is_superuser": False,
                "extra_data": {"department": "IT"}
            }
        }



class UserUpdateRequest(BaseModel):

    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None
    role_id: Optional[UUID] = Field(None, description="Role ID to update")
    location: Optional[str] = Field(None, max_length=255)

    extra_data: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "Updated Name",
                "phone_number": "+9876543210",
                "extra_data": {"theme": "dark"}
            }
        }
    )


class UserResponse(BaseModel):
    id: UUID = Field(..., description="User ID")
    employee_id: Optional[str] = Field(None, description="Employee ID")
    email: str = Field(..., description="User email")
    full_name: Optional[str] = Field(None, description="User full name")
    phone_number: Optional[str] = Field(None, description="User phone number")
    location: Optional[str] = Field(None, description="User location")
    bio: Optional[str] = Field(None, description="User bio")
    date_of_birth: Optional[date] = Field(None, description="User date of birth")
    is_active: bool = Field(..., description="User active status")
    is_superuser: bool = Field(..., description="Superuser status")
    role_id: Optional[UUID] = Field(None, description="Role ID")
    role_name: Optional[str] = Field(None, description="Role name")
    profile_picture_url: Optional[str] = Field(None, description="User profile picture URL")
    joined_date: Optional[datetime] = Field(None, description="joined date of user")
    is_email_verified: bool = Field(..., description="Email verification status")
    email_verified_at: Optional[datetime] = Field(None, description="Email verification timestamp")
    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")
    last_login_ip: Optional[str] = Field(None, description="Last login IP address")
    is_gold: bool = Field(False, description="User gold loyalty status")
    is_vip: bool = Field(False, description="User VIP loyalty status")
    bookings_count: int = Field(0, description="Total completed or confirmed bookings count")
    remaining_to_gold: Optional[int] = Field(None, description="Remaining bookings to reach gold tier")
    remaining_to_vip: Optional[int] = Field(None, description="Remaining bookings to reach VIP tier")
    created_at: Optional[datetime] = Field(None, description="User creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="User last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "full_name": "John Doe",
                "phone_number": "+1234567890",
                "joined_date": "12/12/2026",
                "is_active": True,
                "is_superuser": False,
                "role_id": "3e5bb683-0dbf-4af7-8ab0-35936c36791e",  # UUID example
                "role_name": "vendor",
                "is_email_verified": True,
                "email_verified_at": "2024-01-15T10:30:00Z",
                "last_login_at": "2024-01-20T08:15:00Z",
                "last_login_ip": "192.168.1.1",
                "extra_data": {"preferences": {"theme": "dark"}},
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-20T08:15:00Z"
            }
        }


class UserDetailResponse(UserResponse):

    failed_login_attempts: int = Field(..., description="Failed login attempt count")
    locked_until: Optional[datetime] = Field(None, description="Account lock expiry time")
    
    roles: list = []
    permissions: list = []
    extra_data: Optional[Dict[str, Any]] = None


# ============================================
# User List / Filter Schemas
# ============================================

class UserFilterParams(BaseModel):

    search: Optional[str] = Field(None, description="Search by email or full name")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    is_superuser: Optional[bool] = Field(None, description="Filter by superuser status")
    is_email_verified: Optional[bool] = Field(None, description="Filter by email verification")
    role: Optional[UserRoleFilter] = Field(None, description="Filter by role (customer, vendor, staff, admin)")
    status: Optional[UserStatusFilter] = Field(None, description="Filter by status (active, inactive, all)")
    segment: Optional[UserSegment] = Field(None, description="Filter by user segment (new, active, vip, all)")
    created_from: Optional[datetime] = Field(None, description="Created from date")
    created_to: Optional[datetime] = Field(None, description="Created to date")



class UserProfileUpdateRequest(BaseModel):

    email: Optional[EmailStr] = Field(None, description="User email address")
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=255)

    extra_data: Optional[Dict[str, Any]] = None



class UserLockRequest(BaseModel):

    reason: Optional[str] = Field(None, description="Lock reason")
    lock_duration_minutes: int = Field(
        30, ge=1, description="Lock duration in minutes"
    )


class UserUnlockRequest(BaseModel):

    reason: Optional[str] = Field(None, description="Unlock reason")










class RoleResponse(BaseModel):
    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)


class CurrentUserResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    date_of_birth: Optional[date] = None
    is_active: bool
    is_superuser: bool
    is_email_verified: bool
    roles: List[RoleResponse] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    profile_picture_url: Optional[str] = None
    is_gold: bool = False
    is_vip: bool = False
    bookings_count: int = 0
    remaining_to_gold: Optional[int] = None
    remaining_to_vip: Optional[int] = None
    
    # Stats
    actions_taken: int = 0
    time_active: str = "0h"
    approvals: int = 0
    revenue_impact: str = "PKR 0"
    
    recent_activities: List[RecentActivity] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# ============================================
# User Statistics Schemas
# ============================================

class UserStats(BaseModel):
    """User statistics schema"""
    total_users: int = Field(..., description="Total number of users")
    active_users: int = Field(..., description="Number of active users")
    inactive_users: int = Field(..., description="Number of inactive users")
    new_users: int = Field(0, description="Number of new users this month")
    vip_users: int = Field(0, description="Number of VIP users")
    vendors: int = Field(..., description="Number of users with vendor role")

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """Response schema for list users endpoint with statistics"""
    success: bool = Field(True, description="Whether the operation was successful")
    message: Optional[str] = Field(None, description="Human-readable message")
    data: List[UserResponse] = Field(..., description="List of users")
    meta: PaginationMeta = Field(..., description="Pagination metadata")
    stats: UserStats = Field(..., description="User statistics")

    model_config = ConfigDict(from_attributes=True)