from datetime import date as dt_date, datetime, time as dt_time
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RiderItemCreateRequest(BaseModel):
    rider_id: UUID
    item_name: str = Field(..., min_length=1, max_length=255)
    quantity: float = Field(..., gt=0)
    price: float = Field(..., ge=0)
    weight: float = Field(..., gt=0)
    discount: float = Field(0, ge=0, le=100, description="Discount percentage (0-100)")
    date: dt_date
    time: dt_time


class RiderItemUpdateRequest(BaseModel):
    rider_id: Optional[UUID] = None
    item_name: Optional[str] = Field(None, min_length=1, max_length=255)
    quantity: Optional[float] = Field(None, gt=0)
    price: Optional[float] = Field(None, ge=0)
    weight: Optional[float] = Field(None, gt=0)
    discount: Optional[float] = Field(None, ge=0, le=100, description="Discount percentage (0-100)")
    date: Optional[dt_date] = None
    time: Optional[dt_time] = None


class RiderItemResponse(BaseModel):
    id: UUID
    user_id: UUID
    rider_id: UUID
    invoice_number: str
    item_name: str
    quantity: float
    price: float
    weight: float
    discount: float
    subtotal: float
    total: float
    date: dt_date
    time: dt_time
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
