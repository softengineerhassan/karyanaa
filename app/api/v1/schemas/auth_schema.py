
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator

from app.api.v1.schemas.common_schema import BaseSchema


class RecentActivity(BaseModel):
    action: str
    subject: str
    time_ago: str
    timestamp: str



class LoginRequest(BaseModel):
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")
    device_id: Optional[str] = Field(None, description="Device identifier for tracking")
    fcm_token: Optional[str] = Field(None, description="Firebase Cloud Messaging token for push notifications")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!",
                "device_id": "mobile-app-ios-v1.0",
                "fcm_token": "YOUR_FCM_TOKEN"
            }
        }
    )


class TokenResponse(BaseModel):
    
    access_token: str = Field(..., description="RS256 JWT access token")
    refresh_token: str = Field(..., description="RS256 JWT refresh token")
    token_type: str = Field("Bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiry in seconds")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "Bearer",
                "expires_in": 900
            }
        }
    )


class RefreshTokenRequest(BaseModel):
    
    refresh_token: str = Field(..., description="Valid refresh token")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    )


class LogoutRequest(BaseModel):
    
    refresh_token: Optional[str] = Field(None, description="Refresh token to revoke")
    revoke_all: bool = Field(False, description="Revoke all user sessions")


class RegisterRequest(BaseModel):
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    full_name: str = Field(..., min_length=2, max_length=255, description="User full name")
    phone_number: Optional[str] = Field(None, max_length=20, description="User phone number")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "full_name": "John Doe",
                "phone_number": "+1234567890"
            }
        }
    )


class RegisterResponse(BaseModel):
    
    user_id: UUID = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email")
    full_name: str = Field(..., description="User full name")
    is_email_verified: bool = Field(False, description="Email verification status")
    message: str = Field(..., description="Registration success message")
    
    model_config = ConfigDict(from_attributes=True)


class EmailVerificationRequest(BaseModel):
    
    token: str = Field(..., description="Email verification token")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "token": "abc123def456ghi789jkl012mno345"
            }
        }
    )


class VerifyOTPRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    code: str = Field(..., min_length=4, max_length=10, description="OTP code")


class ResendOTPRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")


class ResendVerificationRequest(BaseModel):
    
    email: EmailStr = Field(..., description="User email address")


class ForgotPasswordRequest(BaseModel):
    
    email: EmailStr = Field(..., description="User email address")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com"
            }
        }
    )

class VerifyResetOTPRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    code: str = Field(..., min_length=4, max_length=4, description="4-digit OTP code")

class ResetOTPResponse(BaseModel):
    reset_token: str = Field(..., description="Short-lived token for password reset")


class ResetPasswordRequest(BaseModel):
    
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "token": "abc123def456ghi789jkl012mno345",
                "new_password": "NewSecurePass123!"
            }
        }
    )


class ChangePasswordRequest(BaseModel):
    
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class RoleResponse(BaseModel):
    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)


class CurrentUserResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: bool
    is_superuser: bool
    is_email_verified: bool
    created_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    profile_picture_url: Optional[str] = None
    
    # Stats
    actions_taken: int = 0
    time_active: str = "0h"
    approvals: int = 0
    revenue_impact: str = "AED 0"

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "full_name": "John Doe",
                "phone_number": "+971500000000",
                "is_active": True,
                "is_superuser": False,
                "is_email_verified": True,
                "created_at": "2026-03-28T10:00:00Z",
                "last_login_at": "2026-03-28T11:00:00Z",
                "profile_picture_url": None,
                "actions_taken": 0,
                "time_active": "2h",
                "approvals": 0,
                "revenue_impact": "AED 0.0"
            }
        },
    )


# ============================================
# JWKS Schema
# ============================================

class JWKSchema(BaseModel):
    
    kty: str = Field(..., description="Key type (RSA)")
    use: str = Field(..., description="Public key use (sig)")
    kid: str = Field(..., description="Key ID")
    alg: str = Field(..., description="Algorithm (RS256)")
    n: str = Field(..., description="Modulus (base64url)")
    e: str = Field(..., description="Exponent (base64url)")


class JWKSResponse(BaseModel):
    
    keys: List[JWKSchema] = Field(..., description="List of JWK public keys")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "keys": [
                    {
                        "kty": "RSA",
                        "use": "sig",
                        "kid": "OMNIA-auth-2024",
                        "alg": "RS256",
                        "n": "0vx7agoebGcQSuuPiLJXZptN9nndrQmbXEps2aiAFbWhM...",
                        "e": "AQAB"
                    }
                ]
            }
        }
    )



class ActiveSessionSchema(BaseModel):
    
    id: UUID = Field(..., description="Session ID")
    device_info: Optional[str] = Field(None, description="Device information")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent")
    created_at: datetime = Field(..., description="Session creation time")
    expires_at: datetime = Field(..., description="Session expiration time")
    is_current: bool = Field(False, description="Whether this is the current session")
    
    model_config = ConfigDict(from_attributes=True)


class ActiveSessionsResponse(BaseModel):
    
    sessions: List[ActiveSessionSchema] = Field(..., description="List of active sessions")
    total: int = Field(..., description="Total number of active sessions")



class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int



class UserPublicResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: bool
    is_superuser: bool
    is_email_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None
    profile_picture_url: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "full_name": "John Doe",
                "phone_number": "+971500000000",
                "is_active": True,
                "is_superuser": False,
                "is_email_verified": True,
                "created_at": "2026-03-28T10:00:00Z",
                "last_login_at": "2026-03-28T11:00:00Z",
                "profile_picture_url": None
            }
        },
    )


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int

    user: UserPublicResponse
    

