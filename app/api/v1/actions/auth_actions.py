from typing import Optional
from uuid import UUID
from fastapi import HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.response import success_response
from app.core import security
# from app.core.response import success_response  <-- Removed top level import
from app.api.v1.schemas.auth_schema import (
    LoginRequest,
    RefreshTokenRequest,
    LogoutRequest,
    RegisterRequest,
    ChangePasswordRequest,
    VerifyOTPRequest,
    ResendOTPRequest,
    ForgotPasswordRequest,
    VerifyResetOTPRequest,
    ResetOTPResponse,
    ResetPasswordRequest
)
from app.api.v1.schemas.common_schema import StandardResponse
from app.utils.exceptions import (
    InvalidCredentialsError,
    UserInactiveError,
    UserLockedError,
    UserAlreadyExistsError,
    InvalidTokenError,
    ExpiredTokenError,
    EmailNotVerifiedError
)

class AuthActions:
    
    @staticmethod
    async def login(request: Request, login_data: LoginRequest, session: Session):
        from app.services.auth_service import AuthService
        auth_service = AuthService(session)
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        try:
            response_data = await auth_service.login(
                email=login_data.email,
                password=login_data.password,
                device_id=login_data.device_id,
                fcm_token=login_data.fcm_token,
                ip_address=client_ip,
                user_agent=user_agent
            )
            return success_response(
                data=response_data,
                message="Login successful"
            )
        except (InvalidCredentialsError, UserInactiveError, UserLockedError, EmailNotVerifiedError) as e:
            # Re-raise to let the global executive handler in main.py handle it (to include 'details')
            raise e
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    def refresh_token(refresh_data: RefreshTokenRequest, session: Session):
        from app.services.auth_service import AuthService
        auth_service = AuthService(session)
        try:
            response_data = auth_service.refresh_token(refresh_data.refresh_token)
            return success_response(
                data=response_data,
                message="Token refreshed successfully"
            )
        except (InvalidTokenError, ExpiredTokenError, UserInactiveError) as e:
            raise HTTPException(status_code=401, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @staticmethod
    async def verify_otp(data: VerifyOTPRequest, session: Session):
        from app.services.auth_service import AuthService
        auth_service = AuthService(session)
        success = await auth_service.verify_email_otp(email=data.email, code=data.code)
        if not success:
            raise HTTPException(status_code=400, detail="Invalid or expired verification code")
        return success_response(message="Email verified successfully")

    @staticmethod
    async def resend_otp(data: ResendOTPRequest, session: Session):
        from app.services.auth_service import AuthService
        auth_service = AuthService(session)
        try:
            await auth_service.resend_verification_otp(email=data.email)
            return success_response(message="Verification code resent successfully")
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @staticmethod
    def logout(logout_data: LogoutRequest, current_user_id: UUID, session: Session):
        from app.services.auth_service import AuthService
        auth_service = AuthService(session)
        auth_service.logout(
            user_id=current_user_id,
            refresh_token=logout_data.refresh_token,
            revoke_all=logout_data.revoke_all
        )
        return success_response(message="Logged out successfully")
    
    @staticmethod
    async def register(register_data: RegisterRequest, session: Session):
        from app.services.auth_service import AuthService
        auth_service = AuthService(session)
        try:
            response_data = await auth_service.register_user(
                email=register_data.email,
                password=register_data.password,
                full_name=register_data.full_name,
                phone_number=register_data.phone_number,
            )
            return success_response(
                data=response_data,
                message="User registered successfully",
                status_code=201
            )
        except UserAlreadyExistsError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @staticmethod
    def change_password(change_data: ChangePasswordRequest, current_user_id: UUID, session: Session):
        from app.services.auth_service import AuthService
        auth_service = AuthService(session)
        try:
            auth_service.change_password(
                user_id=current_user_id,
                current_password=change_data.current_password,
                new_password=change_data.new_password
            )
            return success_response(message="Password changed successfully")
        except InvalidCredentialsError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @staticmethod
    def get_current_user_profile(current_user_id: UUID, session: Session):
        from app.repos.user_repository import UserRepository
        from app.api.v1.mappers.user_mapper import map_user_to_current_user_response

        user_repo = UserRepository(session)
        try:
            user = user_repo.get_by_id(current_user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User profile not found")

            user_data = map_user_to_current_user_response(user, bookings_count=0, session=None)
            return success_response(data=user_data)
        except Exception as e:
            raise HTTPException(status_code=404, detail="User profile not found")

    @staticmethod
    async def forgot_password(data: ForgotPasswordRequest, session: Session):
        from app.services.auth_service import AuthService
        auth_service = AuthService(session)
        await auth_service.request_password_reset(data.email)
        return success_response(message="If an account exists, a reset code has been sent.")

    @staticmethod
    async def verify_reset_otp(data: VerifyResetOTPRequest, session: Session):
        from app.services.auth_service import AuthService
        auth_service = AuthService(session)
        try:
            token = await auth_service.verify_reset_otp(data.email, data.code)
            return success_response(
                data=ResetOTPResponse(reset_token=token),
                message="Reset code verified successfully"
            )
        except InvalidCredentialsError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    async def reset_password(data: ResetPasswordRequest, session: Session):
        from app.services.auth_service import AuthService
        auth_service = AuthService(session)
        try:
            await auth_service.reset_password_with_token(data.token, data.new_password)
            return success_response(message="Password reset successfully")
        except (InvalidTokenError, ExpiredTokenError) as e:
            raise HTTPException(status_code=401, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
