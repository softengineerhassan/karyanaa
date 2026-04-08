from typing import Any
from fastapi import APIRouter, status

from app.api.v1.handlers import UsersHandler
from app.api.v1.schemas import (
    StandardResponse,
    PaginatedResponse,
)
from app.api.v1.schemas.user_schema import (
    UserResponse,
    UserDetailResponse,
    CurrentUserResponse,
    UserListResponse,
)

router = APIRouter(prefix="/users", tags=["Users"])

router.get("", response_model=StandardResponse[UserListResponse], status_code=status.HTTP_200_OK)(UsersHandler.list_users)
router.post("", response_model=StandardResponse[UserResponse], status_code=status.HTTP_201_CREATED)(UsersHandler.create_user)
router.get("/{user_id}", response_model=StandardResponse[UserDetailResponse], status_code=status.HTTP_200_OK)(UsersHandler.get_user)
router.put("/{user_id}", response_model=StandardResponse[UserResponse], status_code=status.HTTP_200_OK)(UsersHandler.update_user)
router.delete("/{user_id}", response_model=StandardResponse[None], status_code=status.HTTP_200_OK)(UsersHandler.delete_user)
router.put("/me/profile", response_model=StandardResponse[CurrentUserResponse], status_code=status.HTTP_200_OK, summary="Update own profile", description="Update profile information. Supporting file upload for profile picture.")(UsersHandler.update_own_profile)
router.patch("/me/profile", response_model=StandardResponse[CurrentUserResponse], status_code=status.HTTP_200_OK, summary="Update own profile (JSON)", description="Update profile fields using JSON payload.")(UsersHandler.update_own_profile_json)
router.post("/me/profile-picture", response_model=StandardResponse[CurrentUserResponse], status_code=status.HTTP_200_OK, summary="Upload profile picture", description="Dedicated endpoint to upload/update profile picture.")(UsersHandler.upload_profile_picture)


router.post("/{user_id}/lock", response_model=StandardResponse[None], status_code=status.HTTP_200_OK)(UsersHandler.lock_user_account)
router.post("/{user_id}/unlock", response_model=StandardResponse[None], status_code=status.HTTP_200_OK)(UsersHandler.unlock_user_account)


router.get("/{user_id}/stats", response_model=StandardResponse[Any], status_code=status.HTTP_200_OK)(UsersHandler.get_user_stats)
