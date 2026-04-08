from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RiderProfileCreateRequest(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    phone_number: str = Field(..., min_length=5, max_length=20)
    email: Optional[EmailStr] = None
    profile_image: Optional[str] = Field(None, max_length=500)


class RiderProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone_number: Optional[str] = Field(None, min_length=5, max_length=20)
    email: Optional[EmailStr] = None
    profile_image: Optional[str] = Field(None, max_length=500)


class RiderProfileResponse(BaseModel):
    id: UUID
    owner_user_id: UUID
    full_name: str
    phone_number: str
    email: Optional[EmailStr] = None
    profile_image: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
