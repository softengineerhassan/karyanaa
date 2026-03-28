from typing import Optional
from uuid import UUID
from fastapi import Depends, Query, File, UploadFile, Form
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user, get_current_superuser, get_pagination_params
from app.models.user import User
from app.api.v1.actions import UsersActions
from app.api.v1.enums.user_enum import UserStatusFilter, UserSegment
from app.api.v1.schemas.user_schema import (
    UserCreateRequest,
    UserUpdateRequest,
    UserProfileUpdateRequest,
    UserLockRequest,
    UserUnlockRequest,
)


class UsersHandler:
    
    @staticmethod
    def list_users(
        search: Optional[str] = Query(None, description="Search by email or name"),
        is_active: Optional[bool] = Query(None, description="Filter by active status"),
        is_superuser: Optional[bool] = Query(None, description="Filter by superuser status"),
        is_email_verified: Optional[bool] = Query(None, description="Filter by email verification"),
        role_id: Optional[UUID] = Query(None, description="Filter by role ID (UUID)"),
        status: Optional[UserStatusFilter] = Query(None, description="Filter by status (active, inactive, all)"),
        segment: Optional[UserSegment] = Query(None, description="Filter by user segment (new, active, vip, all)"),
        pagination: dict = Depends(get_pagination_params),
        session: Session = Depends(get_db),
        current_user = Depends(get_current_user),
    ):
        return UsersActions.list_users(search, is_active, is_superuser, is_email_verified, role_id, status, segment, pagination, session)
    
    @staticmethod
    def create_user(
        user_data: UserCreateRequest,
        session: Session = Depends(get_db),
        current_user = Depends(get_current_user),
    ):
        return UsersActions.create_user(user_data, session)
    
    
    @staticmethod
    def get_user(
        user_id: UUID,
        session: Session = Depends(get_db),
        current_user = Depends(get_current_user),
    ):
        return UsersActions.get_user(user_id, session)
    
    @staticmethod
    def update_user(
        user_id: UUID,
        user_data: UserUpdateRequest,
        session: Session = Depends(get_db),
        current_user = Depends(get_current_user),
    ):
        return UsersActions.update_user(user_id, user_data, session)
    
    @staticmethod
    def delete_user(
        user_id: UUID,
        permanent: bool = Query(False, description="Permanently delete user"),
        session: Session = Depends(get_db),
        current_user = Depends(get_current_user),
    ):
        return UsersActions.delete_user(user_id, permanent, current_user.id, session)
    
    @staticmethod
    def update_own_profile(
        full_name: Optional[str] = Form(None),
        phone_number: Optional[str] = Form(None),
        location: Optional[str] = Form(None),
        bio: Optional[str] = Form(None),
        date_of_birth: Optional[str] = Form(None, description="Date of birth (YYYY-MM-DD)"),
        profile_picture: UploadFile = File(None, description="The user's profile picture file"),
        session: Session = Depends(get_db),
        current_user = Depends(get_current_user),
    ):
        from datetime import date
        profile_data = {}
        if full_name is not None:
            profile_data["full_name"] = full_name
        if phone_number is not None:
            profile_data["phone_number"] = phone_number
        if location is not None:
            profile_data["location"] = location
        if bio is not None:
            profile_data["bio"] = bio
        if date_of_birth is not None:
            try:
                profile_data["date_of_birth"] = date.fromisoformat(date_of_birth)
            except ValueError:
                from fastapi import HTTPException
                raise HTTPException(status_code=400, detail="date_of_birth must be in YYYY-MM-DD format")

        return UsersActions.update_own_profile(profile_data, profile_picture, current_user.id, session)
    
    @staticmethod
    def upload_profile_picture(
        profile_picture: UploadFile = File(..., description="The profile picture file to upload"),
        session: Session = Depends(get_db),
        current_user = Depends(get_current_user),
    ):
        return UsersActions.update_own_profile({}, profile_picture, current_user.id, session)

    @staticmethod
    def lock_user_account(
        user_id: UUID,
        lock_data: UserLockRequest,
        session: Session = Depends(get_db),
        current_user = Depends(get_current_user),
    ):
        return UsersActions.lock_user_account(user_id, lock_data, current_user.id, session)
    
    @staticmethod
    def unlock_user_account(
        user_id: UUID,
        unlock_data: UserUnlockRequest,
        session: Session = Depends(get_db),
        current_user = Depends(get_current_user),
    ):
        return UsersActions.unlock_user_account(user_id, session)
    
    @staticmethod
    def get_user_stats(
        user_id: UUID,
        session: Session = Depends(get_db),
        current_user = Depends(get_current_user),
    ):
        return UsersActions.get_user_stats(user_id, session)
