from fastapi import APIRouter, status
from app.api.v1.handlers.auth_handler import AuthHandler
from app.api.v1.schemas.auth_schema import (
    LoginResponse,
    RefreshTokenResponse,
    RegisterResponse,
    CurrentUserResponse,
    JWKSResponse,
    ForgotPasswordRequest,
    VerifyResetOTPRequest,
    ResetOTPResponse,
    ResetPasswordRequest
)
from app.api.v1.schemas.common_schema import StandardResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

router.post("/login", response_model=StandardResponse[LoginResponse], status_code=status.HTTP_200_OK)(AuthHandler.login)
router.post("/refresh", response_model=StandardResponse[RefreshTokenResponse], status_code=status.HTTP_200_OK)(AuthHandler.refresh_token)
router.post("/logout", response_model=StandardResponse[None], status_code=status.HTTP_200_OK)(AuthHandler.logout)
router.post("/register", response_model=StandardResponse[RegisterResponse], status_code=status.HTTP_201_CREATED)(AuthHandler.register)
router.post("/verify-otp", response_model=StandardResponse[None], status_code=status.HTTP_200_OK)(AuthHandler.verify_otp)
router.post("/resend-otp", response_model=StandardResponse[None], status_code=status.HTTP_200_OK)(AuthHandler.resend_otp)
router.post("/change-password", response_model=StandardResponse[None], status_code=status.HTTP_200_OK)(AuthHandler.change_password)

router.post("/forgot-password", response_model=StandardResponse[None], status_code=status.HTTP_200_OK)(AuthHandler.forgot_password)
router.post("/verify-reset-otp", response_model=StandardResponse[ResetOTPResponse], status_code=status.HTTP_200_OK)(AuthHandler.verify_reset_otp)
router.post("/reset-password", response_model=StandardResponse[None], status_code=status.HTTP_200_OK)(AuthHandler.reset_password)
router.get("/me", response_model=StandardResponse[CurrentUserResponse], status_code=status.HTTP_200_OK)(AuthHandler.get_current_user_profile)
router.get("/.well-known/jwks.json", response_model=JWKSResponse, status_code=status.HTTP_200_OK)(AuthHandler.get_jwks)
router.get("/jwks.json", response_model=JWKSResponse, status_code=status.HTTP_200_OK, include_in_schema=False)(AuthHandler.get_jwks)
