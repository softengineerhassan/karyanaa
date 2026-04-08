from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.api.v1.schemas.dashboard_schema import (
    DashboardLowStockItem,
    DashboardMetric,
    DashboardRecentSale,
    DashboardSummaryResponse,
    DashboardTrendPoint,
)
from app.models.inventory import Product, StockBatch
from app.models.sales import Customer, Sale


class DashboardActions:
    def __init__(self, session: Session):
        self.session = session

    def get_summary(self) -> DashboardSummaryResponse:
        today = date.today()
        start_day = today - timedelta(days=6)

        total_sales = self.session.execute(
            select(func.coalesce(func.sum(Sale.grand_total), 0)).where(
                and_(Sale.deleted_at.is_(None), Sale.status != "cancelled")
            )
        ).scalar_one()

        customer_count = self.session.execute(
            select(func.count(Customer.id)).where(
                and_(Customer.deleted_at.is_(None), Customer.is_active.is_(True))
            )
        ).scalar_one()

        stock_rows = self.session.execute(
            select(
                Product.id,
                Product.name,
                Product.sku,
                Product.minimum_stock_alert,
                Product.track_inventory,
                func.coalesce(func.sum(StockBatch.quantity_available), 0).label("available_quantity"),
            )
            .select_from(Product)
            .outerjoin(StockBatch, StockBatch.product_id == Product.id)
            .where(and_(Product.deleted_at.is_(None), Product.is_active.is_(True)))
            .group_by(Product.id)
        ).all()

        low_stock_items = []
        low_stock_count = 0
        out_of_stock_count = 0
        for row in stock_rows:
            if not row.track_inventory:
                continue
            available_quantity = Decimal(str(row.available_quantity or 0))
            minimum_stock_alert = Decimal(str(row.minimum_stock_alert or 0))
            if available_quantity <= 0:
                out_of_stock_count += 1
            if minimum_stock_alert > 0 and available_quantity <= minimum_stock_alert:
                low_stock_count += 1
                low_stock_items.append(
                    DashboardLowStockItem(
                        id=row.id,
                        name=row.name,
                        sku=row.sku,
                        available_quantity=available_quantity,
                        minimum_stock_alert=minimum_stock_alert,
                    )
                )

        trend_map: dict[str, dict[str, Decimal]] = {
            (start_day + timedelta(days=index)).isoformat(): {"gross_sales": Decimal("0"), "net_revenue": Decimal("0")}
            for index in range(7)
        }

        trend_rows = self.session.execute(
            select(
                Sale.sale_date,
                func.coalesce(func.sum(Sale.grand_total), 0).label("gross_sales"),
                func.coalesce(func.sum(Sale.paid_amount), 0).label("net_revenue"),
            )
            .where(
                and_(
                    Sale.deleted_at.is_(None),
                    Sale.status != "cancelled",
                    Sale.sale_date >= start_day,
                )
            )
            .group_by(Sale.sale_date)
            .order_by(Sale.sale_date)
        ).all()

        for row in trend_rows:
            key = row.sale_date.isoformat()
            if key in trend_map:
                trend_map[key] = {
                    "gross_sales": Decimal(str(row.gross_sales or 0)),
                    "net_revenue": Decimal(str(row.net_revenue or 0)),
                }

        recent_sales_rows = self.session.execute(
            select(Sale, Customer.name.label("customer_name"))
            .join(Customer, Customer.id == Sale.customer_id)
            .where(and_(Sale.deleted_at.is_(None), Sale.status != "cancelled"))
            .order_by(Sale.created_at.desc())
            .limit(5)
        ).all()

        recent_sales = [
            DashboardRecentSale(
                id=sale.id,
                sale_number=sale.sale_number,
                invoice_number=sale.invoice_number,
                customer_name=customer_name or "Unknown Customer",
                sale_date=sale.sale_date,
                grand_total=sale.grand_total,
                payment_status=sale.payment_status,
                status=sale.status,
                created_at=sale.created_at,
            )
            for sale, customer_name in recent_sales_rows
        ]

        metrics = [
            DashboardMetric(
                label="Total Sales",
                value=f"AED {Decimal(str(total_sales or 0)):,.2f}",
                meta="All posted sales",
            ),
            DashboardMetric(
                label="Low Stock Alerts",
                value=str(low_stock_count),
                meta="Requires immediate attention",
            ),
            DashboardMetric(
                label="Customers",
                value=f"{customer_count:,}",
                meta="Active loyalty patrons",
            ),
            DashboardMetric(
                label="Out of Stock",
                value=str(out_of_stock_count),
                meta="Inactive SKU listing",
            ),
        ]

        trend = [
            DashboardTrendPoint(
                day=day_key,
                gross_sales=values["gross_sales"],
                net_revenue=values["net_revenue"],
            )
            for day_key, values in trend_map.items()
        ]

        return DashboardSummaryResponse(
            metrics=metrics,
            sales_trend=trend,
            recent_sales=recent_sales,
            low_stock_items=low_stock_items[:5],
            summary_date=today,
        )
