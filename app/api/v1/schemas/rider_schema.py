from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RiderProfileCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    company_name: Optional[str] = Field(None, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=20)


class RiderProfileUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    company_name: Optional[str] = Field(None, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=20)


class RiderProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    email: EmailStr
    company_name: Optional[str] = None
    phone_number: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
