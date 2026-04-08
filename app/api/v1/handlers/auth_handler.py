from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.api.v1.actions.auth_actions import AuthActions
from app.api.v1.schemas.auth_schema import (
    LoginRequest,
    RefreshTokenRequest,
    LogoutRequest,
    RegisterRequest,
    ChangePasswordRequest,
    UpdateOwnProfileRequest,
    VerifyOTPRequest,
    ResendOTPRequest,
    ForgotPasswordRequest,
    VerifyResetOTPRequest,
    ResetPasswordRequest,
)

class AuthHandler: 
    @staticmethod
    def get_jwks():
        return AuthActions.get_jwks()  
    @staticmethod
    async def login(
        request: Request,
        login_data: LoginRequest,
        session: Session = Depends(get_db),
    ):
        return await AuthActions.login(request, login_data, session)
    
    @staticmethod
    def refresh_token(
        refresh_data: RefreshTokenRequest,
        session: Session = Depends(get_db),
    ):
        return AuthActions.refresh_token(refresh_data, session)
    
    @staticmethod
    def logout(
        logout_data: LogoutRequest,
        session: Session = Depends(get_db),
        current_user = Depends(get_current_user),
    ):
        return AuthActions.logout(logout_data, current_user.id, session)
    
    @staticmethod
    async def register(
        register_data: RegisterRequest,
        session: Session = Depends(get_db),
    ):
        return await AuthActions.register(register_data, session)
    
    @staticmethod
    async def verify_otp(
        verify_data: VerifyOTPRequest,
        session: Session = Depends(get_db),
    ):
        return await AuthActions.verify_otp(verify_data, session)

    @staticmethod
    async def resend_otp(
        resend_data: ResendOTPRequest,
        session: Session = Depends(get_db),
    ):
        return await AuthActions.resend_otp(resend_data, session)

    @staticmethod
    async def send_verification_otp(
        resend_data: ResendOTPRequest,
        session: Session = Depends(get_db),
    ):
        return await AuthActions.send_verification_otp(resend_data, session)

    @staticmethod
    def change_password(
        change_data: ChangePasswordRequest,
        session: Session = Depends(get_db),
        current_user = Depends(get_current_user),
    ):
        return AuthActions.change_password(change_data, current_user.id, session)
    
    @staticmethod
    def get_current_user_profile(
        session: Session = Depends(get_db),
        current_user = Depends(get_current_user),
    ):
        return AuthActions.get_current_user_profile(current_user.id, session)

    @staticmethod
    async def update_own_profile(
        profile_data: UpdateOwnProfileRequest,
        session: Session = Depends(get_db),
        current_user = Depends(get_current_user),
    ):
        return await AuthActions.update_own_profile(profile_data, current_user.id, session)

    @staticmethod
    async def forgot_password(
        forgot_data: ForgotPasswordRequest,
        session: Session = Depends(get_db),
    ):
        return await AuthActions.forgot_password(forgot_data, session)

    @staticmethod
    async def verify_reset_otp(
        verify_data: VerifyResetOTPRequest,
        session: Session = Depends(get_db),
    ):
        return await AuthActions.verify_reset_otp(verify_data, session)

    @staticmethod
    async def reset_password(
        reset_data: ResetPasswordRequest,
        session: Session = Depends(get_db),
    ):
        return await AuthActions.reset_password(reset_data, session)
