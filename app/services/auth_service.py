from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta, timezone
from uuid import UUID
import hashlib
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core import security
from app.repos.user_repository import UserRepository
from app.repos.token_repository import TokenRepository
from app.api.v1.schemas.auth_schema import (
    LoginResponse,
    RefreshTokenResponse,
    UserPublicResponse,
    RegisterResponse
)
from app.api.v1.mappers.user_mapper import map_user_to_public_response
from app.utils.exceptions import (
    InvalidCredentialsError,
    UserNotFoundError,
    UserInactiveError,
    UserLockedError,
    UserAlreadyExistsError,
    InvalidTokenError,
    ExpiredTokenError,
    EmailNotVerifiedError
)

class AuthService:

    PLACEHOLDER_EMAIL_DOMAIN = "employee.karyanaa.app"

    def __init__(self, session: Session):
        self.session = session
        self.user_repo = UserRepository(session)
        self.token_repo = TokenRepository(session)

    def _placeholder_email_for_employee(self, employee_id: str) -> str:
        # Keep internal email unique and deterministic without exposing business IDs as raw local-part.
        digest = hashlib.sha1(employee_id.encode("utf-8")).hexdigest()
        return f"emp_{digest}@{self.PLACEHOLDER_EMAIL_DOMAIN}"

    def _has_profile_email(self, user: Any) -> bool:
        if not user.email:
            return False
        email = str(user.email)
        return not (
            email.endswith(f"@{self.PLACEHOLDER_EMAIL_DOMAIN}")
            or email.endswith("@employee.local")
            or email.endswith("@employee.localhost")
        )

    async def login(
        self, 
        employee_id: str, 
        password: str, 
        device_id: Optional[str] = None,
        fcm_token: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> LoginResponse:
        user = self.user_repo.get_by_employee_id(employee_id)
        if not user:
            raise InvalidCredentialsError()

        if user.locked_until and user.locked_until > datetime.utcnow():
            raise UserLockedError()

        if not security.verify_password(password, user.hashed_password):
            self.user_repo.increment_failed_login(user.id)
            self.session.commit()
            raise InvalidCredentialsError()

        if not user.is_active:
            raise UserInactiveError()

        if self._has_profile_email(user) and not user.is_email_verified:
            # Automatically resend verification code
            await self.resend_verification_otp(user.email)
            raise EmailNotVerifiedError("Email not verified. A new verification code has been sent to your email.")

        self.user_repo.reset_failed_login(user.id)
        
        # FCM Token Logic
        if fcm_token:
            user.fcm_token = fcm_token
        
        # Set joined_date on first login if not set
        if user.joined_date is None:
            user.joined_date = datetime.utcnow()
            
        user.last_login_at = datetime.utcnow()
        user.last_login_ip = ip_address
        
        access_token = self._create_token_with_perms(user)
        refresh_token, jti = security.create_refresh_token(user_id=str(user.id))
        
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        self.token_repo.create({
            "user_id": user.id,
            "jti": jti,
            "token_hash": security.hash_token(refresh_token),
            "expires_at": expires_at,
            "device_id": device_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
        })
        self.session.commit()

        user_dto = map_user_to_public_response(user, bookings_count=0, session=None)
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_dto
        )

    def refresh_token(self, refresh_token: str) -> RefreshTokenResponse:
        stored_token = self.token_repo.find_by_token(refresh_token)
        if not stored_token:
            raise InvalidTokenError("Invalid refresh token")
        
        if stored_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise ExpiredTokenError("Refresh token expired")

        user = self.user_repo.get_by_id(stored_token.user_id)
        if not user or not user.is_active:
             raise UserInactiveError("User inactive or not found")

        access_token = self._create_token_with_perms(user)
        new_refresh_token, new_jti = security.create_refresh_token(user_id=str(user.id))

        self.token_repo.delete(stored_token.id) # Revoke old
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        self.token_repo.create({
            "user_id": user.id,
            "jti": new_jti,
            "token_hash": security.hash_token(new_refresh_token),
            "expires_at": expires_at,
            "device_id": stored_token.device_id,
            "ip_address": stored_token.ip_address,
            "user_agent": stored_token.user_agent,
        })
        self.session.commit()
        
        return RefreshTokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    def logout(self, user_id: UUID, refresh_token: Optional[str] = None, revoke_all: bool = False) -> bool:
        if revoke_all:
            self.token_repo.revoke_user_tokens(user_id)
        elif refresh_token:
            stored_token = self.token_repo.find_by_token(refresh_token)
            if stored_token and stored_token.user_id == user_id:
                self.token_repo.delete(stored_token.id)
        self.session.commit()
        return True

    async def register_user(
        self,
        employee_id: str,
        password: str,
        full_name: str,
        phone_number: Optional[str] = None,
        role_id: Optional[UUID] = None,
        assigned_by: Optional[UUID] = None,
    ) -> RegisterResponse:
        if self.user_repo.employee_id_exists(employee_id):
            raise UserAlreadyExistsError("Employee ID already exists")

        resolved_email = self._placeholder_email_for_employee(employee_id)

        security.validate_password_strength(password)
        hashed_password = security.hash_password(password)
        
        user = self.user_repo.create({
            "employee_id": employee_id,
            "email": resolved_email,
            "hashed_password": hashed_password,
            "full_name": full_name,
            "phone_number": phone_number,
            "is_email_verified": False,
        })
        self.session.flush()

        self.session.commit()
        self.session.refresh(user)

        return RegisterResponse(
            user_id=user.id,
            employee_id=user.employee_id,
            email=None,
            full_name=user.full_name or "",
            is_email_verified=user.is_email_verified,
            message="Registration successful. Please update your profile and add your email.",
        )

    async def verify_email_otp(self, email: str, code: str) -> bool:
        user = self.user_repo.get_by_email(email)
        if not user:
            raise UserNotFoundError()

        from app.models.user_otp import UserOTP
        from sqlalchemy import select, and_

        stmt = select(UserOTP).where(
            and_(
                UserOTP.user_id == user.id,
                UserOTP.code == code,
                UserOTP.purpose == "email_verification",
                UserOTP.expires_at > datetime.utcnow()
            )
        )
        otp_record = self.session.execute(stmt).scalar_one_or_none()

        if not otp_record:
            return False

        user.is_email_verified = True
        user.email_verified_at = datetime.utcnow()
        
        # Delete OTP record after use
        self.session.delete(otp_record)
        self.session.commit()
        return True

    async def resend_verification_otp(self, email: str) -> bool:
        user = self.user_repo.get_by_email(email)
        if not user:
            raise UserNotFoundError()

        if user.is_email_verified:
            return True # Already verified

        await self._generate_and_send_otp(user)
        return True

    async def request_password_reset(self, employee_id: str) -> bool:
        """Step 1: Request password reset and send OTP"""
        user = self.user_repo.get_by_employee_id(employee_id)
        if not user:
            # Mask user existence
            return True

        if not self._has_profile_email(user):
            raise ValueError("Please update your profile and add the email address first")

        await self._generate_and_send_otp(user, purpose="password_reset")
        return True

    async def verify_reset_otp(self, employee_id: str, code: str) -> str:
        """Step 2: Verify reset OTP and return a reset token"""
        user = self.user_repo.get_by_employee_id(employee_id)
        if not user:
            raise InvalidCredentialsError("Invalid or expired reset code")

        from app.models.user_otp import UserOTP
        from sqlalchemy import select, and_

        stmt = select(UserOTP).where(
            and_(
                UserOTP.user_id == user.id,
                UserOTP.code == code,
                UserOTP.purpose == "password_reset",
                UserOTP.expires_at > datetime.utcnow()
            )
        )
        otp_record = self.session.execute(stmt).scalar_one_or_none()

        if not otp_record:
            raise InvalidCredentialsError("Invalid or expired reset code")

        # Delete OTP record after use
        self.session.delete(otp_record)
        self.session.commit()

        # Create a short-lived password reset token
        reset_token = security.create_access_token(
            data={"sub": str(user.id), "purpose": "password_reset"},
            expires_delta=timedelta(hours=1)
        )
        return reset_token

    async def reset_password_with_token(self, token: str, new_password: str) -> bool:
        """Step 3: Reset password using the reset token"""
        try:
            payload = security.decode_token(token)
            if payload.get("purpose") != "password_reset":
                raise InvalidTokenError("Invalid token purpose")
            
            user_id = payload.get("sub")
            if not user_id:
                raise InvalidTokenError("Invalid token payload")

            # Update password
            user = self.user_repo.get_by_id(user_id)
            if not user:
                raise InvalidCredentialsError("User not found")

            # Validate strength
            security.validate_password_strength(new_password)
            
            user.hashed_password = security.hash_password(new_password)
            self.session.commit()
            
            # Revoke all current tokens for security
            self.token_repo.revoke_user_tokens(user.id)
            self.session.commit()
            
            return True

        except (ExpiredTokenError, InvalidTokenError) as e:
            raise InvalidTokenError(str(e))

    async def _generate_and_send_otp(self, user: Any, purpose: str = "email_verification") -> str:
        import secrets
        import string
        from app.models.user_otp import UserOTP
        from app.services.email_service import EmailService

        # Generate 4-digit OTP
        code = "".join(secrets.choice(string.digits) for _ in range(4))
        
        # Clean up old OTPs for this purpose
        from sqlalchemy import delete
        self.session.execute(delete(UserOTP).where(UserOTP.user_id == user.id, UserOTP.purpose == purpose))

        # Expiry logic
        expire_hours = settings.EMAIL_VERIFICATION_EXPIRE_HOURS if purpose == "email_verification" else settings.PASSWORD_RESET_EXPIRE_HOURS
        
        expires_at = datetime.utcnow() + timedelta(hours=expire_hours)
        otp_record = UserOTP(
            user_id=user.id,
            code=code,
            purpose=purpose,
            expires_at=expires_at
        )
        self.session.add(otp_record)
        self.session.commit()

        # Send Email based on purpose
        if purpose == "email_verification":
            await EmailService.send_otp_email(user.email, code)
        elif purpose == "password_reset":
            await EmailService.send_password_reset_email(user.email, code)
        
        return code

    def _create_token_with_perms(self, user: Any) -> str:
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "employee_id": user.employee_id,
            "roles": [],
            "permissions": [],
            "is_email_verified": user.is_email_verified,
        }
        return security.create_access_token(token_data)

    def change_password(self, user_id: UUID, current_password: str, new_password: str) -> bool:
        user = self.user_repo.get_by_id(user_id)
        if not user or not security.verify_password(current_password, user.hashed_password):
            raise InvalidCredentialsError("Current password is incorrect")

        if not self._has_profile_email(user):
            raise ValueError("Please update your profile and add the email address first")

        security.validate_password_strength(new_password)
        user.hashed_password = security.hash_password(new_password)
        self.token_repo.revoke_user_tokens(user_id)
        self.session.commit()
        return True
