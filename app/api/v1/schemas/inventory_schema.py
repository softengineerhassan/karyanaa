from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


ProductType = Literal["stockable", "service", "non_stockable"]


class CategoryCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: Optional[str] = Field(None, max_length=120)
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    is_active: bool = True


class CategoryUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = Field(None, max_length=120)
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class CategoryResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UnitCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    symbol: str = Field(..., min_length=1, max_length=20)
    description: Optional[str] = None
    is_active: bool = True


class UnitUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    symbol: Optional[str] = Field(None, min_length=1, max_length=20)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class UnitResponse(BaseModel):
    id: UUID
    name: str
    symbol: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    slug: Optional[str] = Field(None, max_length=180)
    sku: Optional[str] = Field(None, max_length=80)
    barcode: Optional[str] = Field(None, max_length=120)
    category_id: UUID
    brand_id: Optional[UUID] = None
    unit_id: UUID
    purchase_unit_id: Optional[UUID] = None
    sales_unit_id: Optional[UUID] = None
    product_type: ProductType = "stockable"
    track_inventory: bool = True
    has_expiry: bool = False
    has_batch: bool = False
    minimum_stock_alert: Decimal = Field(default=Decimal("0"), ge=0)
    default_purchase_price: Decimal = Field(default=Decimal("0"), ge=0)
    default_selling_price: Decimal = Field(default=Decimal("0"), ge=0)
    tax_percent: Decimal = Field(default=Decimal("0"), ge=0)
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True


class ProductUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    slug: Optional[str] = Field(None, max_length=180)
    sku: Optional[str] = Field(None, max_length=80)
    barcode: Optional[str] = Field(None, max_length=120)
    category_id: Optional[UUID] = None
    brand_id: Optional[UUID] = None
    unit_id: Optional[UUID] = None
    purchase_unit_id: Optional[UUID] = None
    sales_unit_id: Optional[UUID] = None
    product_type: Optional[ProductType] = None
    track_inventory: Optional[bool] = None
    has_expiry: Optional[bool] = None
    has_batch: Optional[bool] = None
    minimum_stock_alert: Optional[Decimal] = Field(default=None, ge=0)
    default_purchase_price: Optional[Decimal] = Field(default=None, ge=0)
    default_selling_price: Optional[Decimal] = Field(default=None, ge=0)
    tax_percent: Optional[Decimal] = Field(default=None, ge=0)
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    sku: Optional[str] = None
    barcode: Optional[str] = None
    category_id: UUID
    category_name: Optional[str] = None
    brand_id: Optional[UUID] = None
    unit_id: UUID
    unit_name: Optional[str] = None
    purchase_unit_id: Optional[UUID] = None
    purchase_unit_name: Optional[str] = None
    sales_unit_id: Optional[UUID] = None
    sales_unit_name: Optional[str] = None
    product_type: str
    track_inventory: bool
    has_expiry: bool
    has_batch: bool
    minimum_stock_alert: Decimal
    default_purchase_price: Decimal
    default_selling_price: Decimal
    tax_percent: Decimal
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
