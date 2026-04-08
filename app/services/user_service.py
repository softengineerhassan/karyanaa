from sqlalchemy import select
from sqlalchemy.orm import selectinload, Session
from typing import Optional, List, Dict, Any, Tuple
from app.api.v1.enums.user_enum import UserStatusFilter, UserSegment
from datetime import datetime, timedelta
from uuid import UUID

from app.core import security
from app.repos.user_repository import UserRepository
from app.api.v1.mappers.user_mapper import map_user_to_user_response, map_user_to_current_user_response, map_user_to_user_detail_response
from app.api.v1.schemas.user_schema import UserResponse, UserStats, UserDetailResponse
from app.api.v1.schemas.auth_schema import CurrentUserResponse
from fastapi import HTTPException, status, UploadFile
import uuid
from app.utils.exceptions import (
    UserNotFoundError,
    UserAlreadyExistsError,
)
from pydantic import EmailStr, TypeAdapter
from app.models.user import User


EMAIL_ADAPTER = TypeAdapter(EmailStr)

class UserService:
    
    def __init__(self, session: Session):
        self.session = session
        self.user_repo = UserRepository(session)

    def _get_completed_bookings_count(self, user_id: UUID) -> int:
        try:
            from app.repos.booking_repository import BookingRepository
        except Exception:
            return 0

        try:
            booking_repo = BookingRepository(self.session)
            counts = booking_repo.get_user_bookings_count_by_status(user_id)
            return counts.get("completed", 0)
        except Exception:
            return 0
    
    def get_user_by_id(self, user_id: UUID) -> CurrentUserResponse:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()

        total_valid_bookings = self._get_completed_bookings_count(user_id)
        
        return map_user_to_current_user_response(user, bookings_count=total_valid_bookings, session=self.session)
    
    def create_user(
        self,
        email: str,
        password: str,
        full_name: str,
        role_id: Optional[UUID],
        phone_number: Optional[str] = None,
        location: Optional[str] = None,
        is_active: bool = True,
        is_superuser: bool = False,
    ) -> UserResponse:
        if self.user_repo.email_exists(email):
            raise UserAlreadyExistsError()
        
        security.validate_password_strength(password)
        hashed_password = security.hash_password(password)
        
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            phone_number=phone_number,
            location=location,
            is_active=is_active,
            is_superuser=is_superuser,
        )

        user = self.user_repo.create(user)

        self.session.commit()
        self.session.refresh(user)
        
        return map_user_to_user_response(user)
    
    def update_user(
        self,
        user_id: UUID,
        update_data: Dict[str, Any]
    ) -> UserResponse:
        user_orm = self.user_repo.get_by_id(user_id)
        if not user_orm:
            raise UserNotFoundError()
        
        
        # Role model is not part of this trimmed codebase; ignore role updates if present.
        if "role_id" in update_data:
            update_data.pop("role_id", None)

        user = self.user_repo.update(user_id, update_data)
        self.session.commit()
        self.session.refresh(user)
        
        return map_user_to_user_response(user)
    
    def soft_delete_user(self, user_id: UUID) -> bool:
        if not self.user_repo.exists(user_id):
            raise UserNotFoundError()
        self.user_repo.soft_delete(user_id)
        return True

    def hard_delete_user(self, user_id: UUID) -> bool:
        if not self.user_repo.exists(user_id, include_deleted=True):
            raise UserNotFoundError()
        self.user_repo.delete(user_id)
        return True
    
    def list_users(
        self,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_superuser: Optional[bool] = None,
        is_email_verified: Optional[bool] = None,
        role_id: Optional[UUID] = None,
        status: Optional[UserStatusFilter] = None,
        segment: Optional[UserSegment] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[UserResponse], int, UserStats]:
        # Handle status filter - if status is provided, it overrides is_active
        active_filter = is_active
        if status is not None:
            if status == UserStatusFilter.ACTIVE:
                active_filter = True
            elif status == UserStatusFilter.INACTIVE:
                active_filter = False
            elif status == UserStatusFilter.ALL:
                active_filter = None  # Show all regardless of status
        
        # Role filtering is unavailable in this codebase variant.
        role_id = None
        
        users, total = self.user_repo.search_users(
            search=search,
            is_active=active_filter,
            is_superuser=is_superuser,
            is_email_verified=is_email_verified,
            role_id=role_id,
            segment=segment,
            limit=limit,
            offset=skip
        )
        
        # Get user statistics
        analytics = self.user_repo.get_analytics_summary()
        stats = UserStats(
            total_users=analytics["all"],
            active_users=analytics["active"],
            inactive_users=self.user_repo.count_inactive_users(),
            new_users=analytics["new"],
            vip_users=analytics["vip"],
            vendors=self.user_repo.count_vendors()
        )
        
        user_responses = []
        for user in users:
            total_valid_bookings = self._get_completed_bookings_count(user.id)
            user_responses.append(map_user_to_user_response(user, bookings_count=total_valid_bookings))
            
        return user_responses, total, stats
    
    def _validate_image(self, file: UploadFile):
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File {file.filename} is not an image"
            )
        
        # Max 5MB
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)
        
        if size > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File {file.filename} is too large (max 5MB)"
            )

    def update_own_profile(
        self,
        user_id: UUID,
        profile_data: Dict[str, Any],
        profile_picture: Optional[UploadFile] = None
    ) -> CurrentUserResponse:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()

        if "email" in profile_data:
            new_email = profile_data.get("email")
            if new_email:
                try:
                    validated_email = str(EMAIL_ADAPTER.validate_python(str(new_email).strip()))
                except Exception:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid email format"
                    )

                if self.user_repo.email_exists(validated_email, exclude_user_id=user_id):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already registered"
                    )

                if user.email != validated_email:
                    profile_data["email"] = validated_email
                    profile_data["is_email_verified"] = False
                    profile_data["email_verified_at"] = None
            else:
                profile_data.pop("email", None)

        if profile_picture:
            self._validate_image(profile_picture)

            try:
                from app.services.s3_service import S3Service
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Profile picture upload service is not configured"
                )
            
            ext = profile_picture.filename.split('.')[-1] if '.' in profile_picture.filename else 'jpg'
            s3_key = f"users/{user_id}/profile/{uuid.uuid4()}.{ext}"
            
            s3_service = S3Service()
            s3_service.upload_fileobj(profile_picture.file, s3_key, profile_picture.content_type)
            
            profile_data["profile_picture"] = s3_key

        updated_user = self.user_repo.update(user_id, profile_data)
        self.session.commit()
        self.session.refresh(updated_user)
        
        total_valid_bookings = self._get_completed_bookings_count(user_id)
        
        return map_user_to_current_user_response(updated_user, bookings_count=total_valid_bookings, session=self.session)
    
    def lock_user_account(
        self,
        user_id: UUID,
        reason: Optional[str] = None
    ) -> bool:
        if not self.user_repo.exists(user_id):
            raise UserNotFoundError()
        
        self.user_repo.update(user_id, {
            "is_active": False,
            "locked_at": datetime.utcnow(),
            "lock_reason": reason,
        })
        self.session.commit()
        return True
    
    def unlock_user_account(
        self,
        user_id: UUID
    ) -> bool:
        if not self.user_repo.exists(user_id):
            raise UserNotFoundError()
        
        self.user_repo.update(user_id, {
            "is_active": True,
            "locked_at": None,
            "lock_reason": None,
            "failed_login_attempts": 0
        })
        self.session.commit()
        return True
    
    def get_user_stats(self, user_id: UUID) -> Dict[str, Any]:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        
        return {
            "user_id": str(user.id),
            "is_active": user.is_active,
            "is_email_verified": user.is_email_verified,
            "failed_login_attempts": user.failed_login_attempts or 0,
            "is_locked": user.locked_until is not None and user.locked_until > datetime.utcnow(),
            "locked_until": user.locked_until.isoformat() if user.locked_until else None,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            "created_at": user.created_at.isoformat(),
        }
