from typing import Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.response import success_response, paginated_response
from app.services.user_service import UserService
from app.api.v1.schemas import PaginatedResponse, StandardResponse, PaginationMeta
from app.api.v1.schemas.user_schema import (
    UserCreateRequest,
    UserUpdateRequest,
    UserProfileUpdateRequest,
    UserLockRequest,
    UserListResponse
)
from app.api.v1.mappers.user_mapper import map_user_to_current_user_response
from app.api.v1.enums.user_enum import UserStatusFilter, UserSegment
from app.utils.exceptions import UserNotFoundError, UserAlreadyExistsError, RoleNotFoundError

class UsersActions:
    
    @staticmethod
    def list_users(
        search: Optional[str],
        is_active: Optional[bool],
        is_superuser: Optional[bool],
        is_email_verified: Optional[bool],
        role_id: Optional[UUID],
        status: Optional[UserStatusFilter],
        segment: Optional[UserSegment],
        pagination: dict,
        session: Session,
    ):
        user_service = UserService(session)
        skip = pagination.get("offset", 0)
        limit = pagination.get("limit", 20)
        page = pagination.get("page", 1)
        page_size = pagination.get("page_size", 20)
        
        try:
            users, total, stats = user_service.list_users(
                search=search,
                is_active=is_active,
                is_superuser=is_superuser,
                is_email_verified=is_email_verified,
                role_id=role_id,
                status=status,
                segment=segment,
                skip=skip,
                limit=limit
            )
        except RoleNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        
        # Calculate pagination metadata
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        meta = PaginationMeta(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
        
        return UserListResponse(
            success=True,
            message="Users retrieved successfully",
            data=users,
            meta=meta,
            stats=stats
        )
    
    @staticmethod
    def create_user(user_data: UserCreateRequest, session: Session):
        user_service = UserService(session)
        try:
            user = user_service.create_user(
                email=user_data.email,
                password=user_data.password,
                full_name=user_data.full_name,
                role_id=user_data.role_id,
                phone_number=user_data.phone_number,
                location=user_data.location,
                is_active=user_data.is_active,
                is_superuser=user_data.is_superuser,
            )
            return success_response(data=user, message="User created successfully", status_code=201)
        except UserAlreadyExistsError:
            raise HTTPException(status_code=400, detail="Email already registered")
        except RoleNotFoundError:
            raise HTTPException(status_code=400, detail="Role not found")
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @staticmethod
    def get_user(user_id: UUID, session: Session):
        user_service = UserService(session)
        try:
            user = user_service.get_user_by_id(user_id)
            return success_response(data=user, message="User retrieved successfully")
        except UserNotFoundError:
            raise HTTPException(status_code=404, detail="User not found")
    
    @staticmethod
    def update_user(user_id: UUID, user_data: UserUpdateRequest, session: Session):
        user_service = UserService(session)
        try:
            update_dict = user_data.model_dump(exclude_unset=True)
            user = user_service.update_user(user_id, update_dict)
            return success_response(data=user, message="User updated successfully")
        except UserNotFoundError:
            raise HTTPException(status_code=404, detail="User not found")
    
    @staticmethod
    def delete_user(
        user_id: UUID,
        permanent: bool,
        current_user_id: UUID,
        session: Session
    ):
        user_service = UserService(session)
        if user_id == current_user_id:
            raise HTTPException(status_code=400, detail="Cannot delete yourself")
            
        try:
            if permanent:
                user_service.hard_delete_user(user_id)
                message = "User permanently deleted"
            else:
                user_service.soft_delete_user(user_id)
                message = "User deleted successfully"
            return success_response(message=message)
        except UserNotFoundError:
            raise HTTPException(status_code=404, detail="User not found")
    
    @staticmethod
    def update_own_profile(profile_data: dict, profile_picture, user_id: UUID, session: Session):
        user = UserService(session).update_own_profile(user_id, profile_data, profile_picture)
        return success_response(data=user, message="Profile updated successfully")
    
    @staticmethod
    def lock_user_account(user_id: UUID, lock_data: UserLockRequest, current_user_id: UUID, session: Session):
        if user_id == current_user_id:
            raise HTTPException(status_code=400, detail="Cannot lock yourself")
            
        user_service = UserService(session)
        try:
            user_service.lock_user_account(user_id, lock_data.reason)
            return success_response(message="User account locked successfully")
        except UserNotFoundError:
            raise HTTPException(status_code=404, detail="User not found")
    
    @staticmethod
    def unlock_user_account(user_id: UUID, session: Session):
        user_service = UserService(session)
        try:
            user_service.unlock_user_account(user_id)
            return success_response(message="User account unlocked successfully")
        except UserNotFoundError:
            raise HTTPException(status_code=404, detail="User not found")
    
    @staticmethod
    def get_user_stats(user_id: UUID, session: Session):
        user_service = UserService(session)
        try:
            stats = user_service.get_user_stats(user_id)
            return success_response(data=stats, message="User statistics retrieved successfully")
        except UserNotFoundError:
            raise HTTPException(status_code=404, detail="User not found")
