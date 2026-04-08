from datetime import date, datetime
from decimal import Decimal
from typing import List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DashboardMetric(BaseModel):
    label: str
    value: str
    meta: str


class DashboardTrendPoint(BaseModel):
    day: str
    gross_sales: Decimal = Field(default=Decimal("0"))
    net_revenue: Decimal = Field(default=Decimal("0"))


class DashboardRecentSale(BaseModel):
    id: UUID
    sale_number: str
    invoice_number: str | None = None
    customer_name: str
    sale_date: date
    grand_total: Decimal
    payment_status: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DashboardLowStockItem(BaseModel):
    id: UUID
    name: str
    sku: str | None = None
    available_quantity: Decimal = Field(default=Decimal("0"))
    minimum_stock_alert: Decimal = Field(default=Decimal("0"))


class DashboardSummaryResponse(BaseModel):
    metrics: List[DashboardMetric]
    sales_trend: List[DashboardTrendPoint]
    recent_sales: List[DashboardRecentSale]
    low_stock_items: List[DashboardLowStockItem]
    summary_date: date
