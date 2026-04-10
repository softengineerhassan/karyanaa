from datetime import date, datetime
from typing import List, Optional, Literal, Annotated
from pydantic import BaseModel, Field
from decimal import Decimal
from uuid import UUID


# Type aliases for decimal validation
PositiveDecimal = Annotated[Decimal, Field(gt=0, decimal_places=2)]
PositiveDecimalQty = Annotated[Decimal, Field(gt=0, decimal_places=3)]
NonNegativeDecimal = Annotated[Decimal, Field(ge=0, decimal_places=2)]
NonNegativeDecimalQty = Annotated[Decimal, Field(ge=0, decimal_places=3)]
TaxPercent = Annotated[Decimal, Field(ge=0, decimal_places=2)]


# ============================================================================
# CUSTOMER SCHEMAS
# ============================================================================


class CustomerCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    phone: Optional[str] = Field(None, max_length=30)
    email: Optional[str] = Field(None, max_length=120)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    opening_balance: NonNegativeDecimal = Decimal("0")
    customer_type: Literal["walk_in", "regular", "wholesale"] = "walk_in"
    notes: Optional[str] = None


class CustomerUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    phone: Optional[str] = Field(None, max_length=30)
    email: Optional[str] = Field(None, max_length=120)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    opening_balance: Optional[NonNegativeDecimal] = None
    customer_type: Optional[Literal["walk_in", "regular", "wholesale"]] = None
    notes: Optional[str] = None


class CustomerResponse(BaseModel):
    id: UUID
    name: str
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    city: Optional[str]
    opening_balance: Decimal
    current_balance: Decimal
    customer_type: str
    notes: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# SALE ITEM SCHEMAS
# ============================================================================


class SaleItemCreateRequest(BaseModel):
    product_id: str
    unit_id: str
    quantity: PositiveDecimalQty
    unit_price: PositiveDecimal
    discount_type: Optional[Literal["flat", "percent"]] = None
    discount_value: NonNegativeDecimal = Decimal("0")
    tax_percent: TaxPercent = Decimal("0")
    notes: Optional[str] = None


class SaleItemResponse(BaseModel):
    id: UUID
    product_id: UUID
    product_name_snapshot: str
    sku_snapshot: Optional[str]
    barcode_snapshot: Optional[str]
    unit_id: UUID
    quantity: Decimal
    unit_price: Decimal
    cost_price_snapshot: Decimal
    discount_type: Optional[str]
    discount_value: Decimal
    discount_amount: Decimal
    tax_percent: Decimal
    tax_amount: Decimal
    line_total: Decimal
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# SALE SCHEMAS
# ============================================================================


class SaleCreateRequest(BaseModel):
    customer_id: str
    sale_date: date
    invoice_number: Optional[str] = None
    payment_method: Literal["cash", "bank_transfer", "easypaisa", "jazzcash", "card", "credit"] = "cash"
    paid_amount: NonNegativeDecimal = Decimal("0")
    other_charges: NonNegativeDecimal = Decimal("0")
    notes: Optional[str] = None
    items: List[SaleItemCreateRequest] = Field(min_length=1)


class SaleResponse(BaseModel):
    id: UUID
    sale_number: str
    customer_id: UUID
    sale_date: date
    invoice_number: Optional[str]
    payment_method: str
    payment_status: str
    subtotal: Decimal
    discount_total: Decimal
    tax_total: Decimal
    other_charges: Decimal
    grand_total: Decimal
    paid_amount: Decimal
    remaining_amount: Decimal
    notes: Optional[str]
    status: str
    created_by: Optional[UUID]
    items: Optional[List[SaleItemResponse]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SaleListResponse(BaseModel):
    id: UUID
    sale_number: str
    customer_id: UUID
    sale_date: date
    invoice_number: Optional[str]
    payment_status: str
    grand_total: Decimal
    paid_amount: Decimal
    remaining_amount: Decimal
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# SALE PAYMENT SCHEMAS
# ============================================================================


class SalePaymentCreateRequest(BaseModel):
    payment_date: date
    amount: PositiveDecimal
    payment_method: Literal["cash", "bank_transfer", "easypaisa", "jazzcash", "card", "credit"]
    reference_number: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class SalePaymentResponse(BaseModel):
    id: UUID
    sale_id: UUID
    customer_id: UUID
    payment_date: date
    amount: Decimal
    payment_method: str
    reference_number: Optional[str]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# INVOICE SCHEMAS
# ============================================================================


class InvoiceCustomerResponse(BaseModel):
    id: UUID
    name: str
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    city: Optional[str]
    customer_type: str


class InvoiceItemResponse(BaseModel):
    product_id: UUID
    product_name: str
    sku: Optional[str]
    barcode: Optional[str]
    quantity: Decimal
    unit_price: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    line_total: Decimal


class InvoicePaymentResponse(BaseModel):
    payment_date: date
    amount: Decimal
    payment_method: str
    reference_number: Optional[str]


class PrintableInvoiceResponse(BaseModel):
    sale_id: UUID
    sale_number: str
    invoice_number: Optional[str]
    sale_date: date
    transaction_datetime: Optional[datetime] = None
    status: str
    payment_status: str
    payment_method: str
    cashier_id: Optional[UUID] = None
    cashier_name: Optional[str] = None

    customer: InvoiceCustomerResponse
    items: List[InvoiceItemResponse]
    payments: List[InvoicePaymentResponse]

    subtotal: Decimal
    discount_total: Decimal
    tax_total: Decimal
    other_charges: Decimal
    grand_total: Decimal
    paid_amount: Decimal
    remaining_amount: Decimal

    notes: Optional[str]
    company_name: str
    generated_at: datetime
