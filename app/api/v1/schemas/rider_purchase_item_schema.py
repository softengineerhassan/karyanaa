from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RiderPurchaseItemCreateRequest(BaseModel):
    rider_profile_id: UUID
    item_name: str = Field(..., min_length=1, max_length=255)
    item_code: Optional[str] = Field(None, max_length=80)
    barcode: Optional[str] = Field(None, max_length=120)
    category: Optional[str] = Field(None, max_length=150)
    brand: Optional[str] = Field(None, max_length=120)
    quantity: Decimal = Field(..., gt=0, decimal_places=3)
    unit: Optional[str] = Field(None, max_length=50)
    unit_size: Optional[Decimal] = Field(None, gt=0, decimal_places=3)
    unit_price: Decimal = Field(..., gt=0, decimal_places=2)
    cost_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    total_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    purchase_date: date
    expiry_date: Optional[date] = None
    batch_number: Optional[str] = Field(None, max_length=100)
    supplier_name: Optional[str] = Field(None, max_length=150)
    supplier_contact: Optional[str] = Field(None, max_length=30)
    status: Optional[str] = Field("delivered", max_length=30)
    payment_status: Optional[str] = Field("paid", max_length=30)
    notes: Optional[str] = None
    created_by: Optional[UUID] = None


class RiderPurchaseItemUpdateRequest(BaseModel):
    rider_profile_id: Optional[UUID] = None
    item_name: Optional[str] = Field(None, min_length=1, max_length=255)
    item_code: Optional[str] = Field(None, max_length=80)
    barcode: Optional[str] = Field(None, max_length=120)
    category: Optional[str] = Field(None, max_length=150)
    brand: Optional[str] = Field(None, max_length=120)
    quantity: Optional[Decimal] = Field(None, gt=0, decimal_places=3)
    unit: Optional[str] = Field(None, max_length=50)
    unit_size: Optional[Decimal] = Field(None, gt=0, decimal_places=3)
    unit_price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    cost_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    total_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    purchase_date: Optional[date] = None
    expiry_date: Optional[date] = None
    batch_number: Optional[str] = Field(None, max_length=100)
    supplier_name: Optional[str] = Field(None, max_length=150)
    supplier_contact: Optional[str] = Field(None, max_length=30)
    status: Optional[str] = Field(None, max_length=30)
    payment_status: Optional[str] = Field(None, max_length=30)
    notes: Optional[str] = None
    created_by: Optional[UUID] = None


class RiderPurchaseItemResponse(BaseModel):
    id: UUID
    owner_user_id: UUID
    rider_profile_id: UUID
    item_name: str
    item_code: Optional[str] = None
    barcode: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    quantity: Decimal
    unit: Optional[str] = None
    unit_size: Optional[Decimal] = None
    unit_price: Decimal
    cost_price: Optional[Decimal] = None
    total_amount: Decimal
    total_price: Decimal
    purchase_date: date
    expiry_date: Optional[date] = None
    batch_number: Optional[str] = None
    supplier_name: Optional[str] = None
    supplier_contact: Optional[str] = None
    status: Optional[str] = None
    payment_status: Optional[str] = None
    notes: Optional[str] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
